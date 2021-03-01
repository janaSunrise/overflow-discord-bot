import discord
from discord.ext.commands import Cog
from loguru import logger

from bot import Bot


class Events(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Log message on guild join."""
        logger.info(f"[GUILD] Joined {guild.name}")

    @Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Log message on guild remove."""
        logger.info(f"[GUILD] Left {guild.name}")
