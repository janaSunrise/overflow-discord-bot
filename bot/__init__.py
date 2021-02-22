import asyncio
import sys
import typing as t
from datetime import datetime

import aiohttp
import discord
from discord.ext.commands import Context
import spotify
from asyncpg.exceptions import InvalidPasswordError
from discord.ext.commands import AutoShardedBot
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from bot import config
from bot.databases import bring_databases_into_scope, DatabaseBase
from bot.databases.prefix import Prefix

# -- Logger configuration --
logger.configure(
    handlers=[
        dict(sink=sys.stdout, format=config.log_format, level=config.log_level),
        dict(sink=config.log_file, format=config.log_format, level=config.log_level, rotation="300 MB")
    ]
)


class Bot(AutoShardedBot):
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the subclass."""
        super().__init__(*args, **kwargs)

        self.default_prefix = config.COMMAND_PREFIX

        self.start_time = datetime.utcnow()
        self.session = None
        self.database = None

        self.initial_call = True

        self.spotify = spotify.Client(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret
        )
        self.spotify_http = spotify.HTTPClient(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret
        )

        self.prefix_dict = {}

    async def is_owner(self, user: discord.User):
        if user.id in config.devs:
            return True

        return await super().is_owner(user)

    async def init_db(self) -> AsyncSession:
        """Initialize the database."""
        bring_databases_into_scope()

        engine = create_async_engine(config.DATABASE_CONN)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(DatabaseBase.metadata.create_all)
        except InvalidPasswordError as exc:
            logger.error("The database password entered is invalid.")
            raise exc
        except ConnectionRefusedError:
            logger.error("Database connection refused. Trying again.")
            await asyncio.sleep(3)
            return await self.init_db()

        return AsyncSession(bind=engine)

    async def load_extensions(self) -> None:
        """Load all listed cogs."""
        from bot.core import loader

        for extension in loader.COGS:
            try:
                self.load_extension(extension)
                logger.info(f"Cog {extension} loaded.")
            except Exception as e:
                logger.error(f"Cog {extension} failed to load with {type(e)}: {e!r}")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Log message on guild join."""
        logger.info(f"{guild.name} joined")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Log message on guild remove."""
        logger.info(f"{guild.name} left")

    async def on_ready(self) -> None:
        if self.initial_call:
            self.initial_call = False
            await self.load_extensions()

            logger.info("Bot is ready")
        else:
            logger.info("Bot connection reinitialized")

        rows = await Prefix.get_prefixes(self.database)
        for row in rows:
            self.prefix_dict[row["ctx_id"]] = row["prefix"]

    def run(self, token: t.Optional[str]) -> None:
        """Run the bot and add missing token check."""
        if not token:
            logger.error("Missing Bot Token!")
        else:
            super().run(token)

    async def start(self, *args, **kwargs) -> None:
        """Starts the bot."""
        self.session = aiohttp.ClientSession()
        self.database = await self.init_db()

        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        logger.debug("Closing bot connection")
        if hasattr(self, "session"):
            await self.session.close()

        if hasattr(self, "database"):
            await self.database.close()

        await super().close()

    async def get_prefix(self, message: discord.Message) -> str:
        """Get the prefix from a message."""
        if message.content.startswith(f"{self.command_prefix}help"):
            return self.default_prefix

        return self.prefix_dict.get(
            self.get_id(message),
            self.default_prefix
        )

    def get_id(self, ctx: Context) -> int:
        """Get a context's id."""
        if ctx.guild:
            return ctx.guild.id
        return ctx.channel.id

    async def confirmation(
            self, ctx, description: str, title: str, color=discord.Color.blurple(), footer: t.Optional[str] = None
    ):
        emojis = {"✅": True, "❌": False}

        embed = discord.Embed(title=title, description=description, color=color)

        if footer is not None:
            embed.set_footer(text=footer)

        message = await ctx.send(embed=embed)
        user = ctx.author

        for emoji in emojis:
            await message.add_reaction(emoji)

        try:
            reaction, user = await self.wait_for(
                "reaction_add",
                check=lambda r, u: (r.message.id == message.id) and (u.id == user.id) and (r.emoji in emojis),
                timeout=30
            )
        except asyncio.TimeoutError:
            confirmed = None
            return
        finally:
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                pass

        confirmed = emojis[reaction.emoji]
        return confirmed
