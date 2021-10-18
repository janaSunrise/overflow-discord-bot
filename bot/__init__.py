import asyncio
import collections
import sys
import typing as t
from datetime import datetime

import aiohttp
import discord
import spotify
from asyncpg.exceptions import InvalidPasswordError
from discord.ext.commands import AutoShardedBot, Context
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from bot import config
from bot.databases import DatabaseBase, bring_databases_into_scope
from bot.databases.prefix import Prefix

# -- Logger configuration --
logger.configure(
    handlers=[
        dict(sink=sys.stdout, format=config.log_format, level=config.log_level),
        dict(
            sink=config.log_file,
            format=config.log_format,
            level=config.log_level,
            rotation=config.log_file_size,
        ),
    ]
)


class Bot(AutoShardedBot):
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the subclass."""
        super().__init__(*args, **kwargs)

        # -- Prefix --
        self.default_prefix = config.COMMAND_PREFIX
        self.prefix_dict = {}

        # -- Bot info --
        self.cluster = kwargs.get("cluster_id")
        self.cluster_count = kwargs.get("cluster_count")
        self.version = kwargs.get("version")

        # -- Start time config --
        self.start_time = datetime.utcnow()

        # -- Sessions config --
        self.session = None
        self.database = None

        # -- Counters config --
        self.bot_counters = collections.defaultdict(collections.Counter)
        self.guild_counters = collections.defaultdict(collections.Counter)

        # -- Startup config --
        self.initial_call = True

        # -- Spotify config --
        self.spotify = spotify.Client(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret,
        )
        self.spotify_http = spotify.HTTPClient(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret,
        )

    async def is_owner(self, user: discord.User) -> bool:
        if user.id in config.devs:
            return True

        return await super().is_owner(user)

    async def init_db(self) -> sessionmaker:
        """Initialize the database."""
        bring_databases_into_scope()

        engine = create_async_engine(config.DATABASE_CONN, pool_size=30, max_overflow=0)

        try:
            async with engine.begin() as conn:
                await conn.run_sync(DatabaseBase.metadata.create_all)
        except InvalidPasswordError as exc:
            logger.critical("The database password entered is invalid.")
            raise exc
        except ConnectionRefusedError:
            logger.error("Database connection refused. Trying again.")
            await asyncio.sleep(3)

            return await self.init_db()

        async_session = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )

        return async_session

    async def load_extensions(self) -> None:
        """Load all listed cogs."""
        from bot.core import loader

        for extension in loader.COGS:
            try:
                self.load_extension(extension)
                logger.info(f"Cog {extension} loaded.")
            except Exception as exc:
                logger.error(
                    f"Cog {extension} failed to load with {type(exc)}: {exc!r}"
                )
                raise exc

    async def on_ready(self) -> None:
        """Functions called when the bot is ready and connected."""
        if self.initial_call:
            self.initial_call = False
            await self.load_extensions()

            logger.info("Bot is ready")
        else:
            logger.info("Bot connection reinitialized")

        rows = await Prefix.get_prefixes(self.database)

        for row in rows:
            self.prefix_dict[row["context_id"]] = [row["prefix"], self.default_prefix]

    def run(self, token: t.Optional[str]) -> None:
        """Run the bot and add missing token check."""
        if not token:
            logger.critical("Missing Bot Token!")
        else:
            super().run(token)

    async def start(self, *args, **kwargs) -> None:
        """Starts the bot."""
        self.session = aiohttp.ClientSession()
        self.database = await self.init_db()

        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        logger.info("Closing bot connection")

        if hasattr(self, "session"):
            await self.session.close()

        await super().close()

    # -- Other methods --
    async def get_msg_prefix(
        self, message: discord.Message, not_print: bool = True
    ) -> str:
        """Get the prefix from a message."""
        if not_print:
            return self.default_prefix

        return self.prefix_dict.get(self.get_id(message), self.default_prefix)

    @staticmethod
    def get_id(message: t.Union[discord.Message, Context]) -> int:
        """Get a context's id."""
        if message.guild:
            return message.guild.id

        return message.channel.id

    async def get_or_fetch_member(
        self, guild: discord.Guild, member_id: int
    ) -> t.Optional[discord.Member]:
        member = guild.get_member(member_id)
        if member is not None:
            return member

        shard = self.get_shard(guild.shard_id)
        if shard.is_ws_ratelimited():
            try:
                member = await guild.fetch_member(member_id)
            except discord.HTTPException:
                return None
            else:
                return member

        members = await guild.query_members(limit=1, user_ids=[member_id], cache=True)
        if not members:
            return None
        return members[0]

    async def resolve_member_ids(
        self, guild: t.Union[int, discord.Guild], member_ids: t.Union[list, tuple]
    ) -> t.AsyncIterable:
        needs_resolution = []
        for member_id in member_ids:
            member = guild.get_member(member_id)
            if member is not None:
                yield member
            else:
                needs_resolution.append(member_id)

        total_need_resolution = len(needs_resolution)
        if total_need_resolution == 1:
            shard = self.get_shard(guild.shard_id)
            if shard.is_ws_ratelimited():
                try:
                    member = await guild.fetch_member(needs_resolution[0])
                except discord.HTTPException:
                    pass
                else:
                    yield member
            else:
                members = await guild.query_members(
                    limit=1, user_ids=needs_resolution, cache=True
                )
                if members:
                    yield members[0]
        elif total_need_resolution <= 100:
            resolved = await guild.query_members(
                limit=100, user_ids=needs_resolution, cache=True
            )
            for member in resolved:
                yield member
        else:
            for index in range(0, total_need_resolution, 100):
                to_resolve = needs_resolution[index : index + 100]
                members = await guild.query_members(
                    limit=100, user_ids=to_resolve, cache=True
                )
                for member in members:
                    yield member
