import typing as t
from datetime import datetime

import aiohttp
import aiosqlite
from discord.ext.commands import AutoShardedBot
import spotify

from bot import config


class Bot(AutoShardedBot):
    def __init__(self, extensions: t.List[str], *args, **kwargs) -> None:
        """Initialize the subclass."""
        super().__init__(*args, **kwargs)

        self.start_time = datetime.utcnow()
        self.session = None

        self.extension_list = extensions
        self.initial_call = True

        self.spotify = spotify.Client(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret
        )
        self.spotify_http = spotify.HTTPClient(
            client_id=config.spotify_client_id,
            client_secret=config.spotify_client_secret
        )

        self.db = None

    async def init_db(self) -> None:
        """Initialize the database."""
        commands = [
            """
            CREATE TABLE IF NOT EXISTS newsfeed (
                guild_id INTEGER NOT NULL UNIQUE,
                channel_id INTEGER NOT NULL UNIQUE
            )
            """
        ]
        self.db = await aiosqlite.connect("overflow-bot.db")

        for command in commands:
            await self.db.execute(command)
            await self.db.commit()

    async def load_extensions(self) -> None:
        """Load all listed cogs."""
        for extension in self.extension_list:
            try:
                self.load_extension(extension)
                print(f"Cog {extension} loaded.")
            except Exception as e:
                print(f"Cog {extension} failed to load with {type(e)}: {e!r}")

    async def on_ready(self) -> None:
        if self.initial_call:
            self.initial_call = False
            await self.load_extensions()

            print("Bot is ready")
        else:
            print("Bot connection reinitialized")

    def run(self, token: t.Optional[str]) -> None:
        """Run the bot and add missing token check."""
        if not token:
            print("Missing Bot Token!")
        else:
            super().run(token)

    async def start(self, *args, **kwargs) -> None:
        """Starts the bot."""
        self.session = aiohttp.ClientSession()
        await self.init_db()
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        print("Closing bot connection")
        if hasattr(self, "session"):
            await self.session.close()

        await super().close()
