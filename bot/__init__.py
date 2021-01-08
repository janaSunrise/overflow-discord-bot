import typing as t
from datetime import datetime

import aiohttp
from discord.ext.commands import AutoShardedBot


class Bot(AutoShardedBot):
    def __init__(self, extensions: t.List[str], *args, **kwargs) -> None:
        """Initialize the subclass."""
        super().__init__(*args, **kwargs)

        self.start_time = datetime.utcnow()
        self.session = None

        self.extension_list = extensions
        self.initial_call = True

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
        if not token:
            print("Missing Bot Token!")
        else:
            super().run(token)

    async def start(self, *args, **kwargs) -> None:
        self.session = aiohttp.ClientSession()
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """Close the bot and do some cleanup."""
        print("Closing bot connection")
        if hasattr(self, "session"):
            await self.session.close()

        await super().close()
