import discord
from discord.ext.commands import (
    Cog, Context, TextChannelConverter, group,
    has_permissions
)

from bot import Bot
from bot.databases.logging import Logging


class LoggingSettings(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(
        invoke_without_command=True, aliases=["log-config", "log-conf", "log-cfg", "logging"]
    )
    @has_permissions(manage_roles=True)
    async def logging_config(self, ctx: Context) -> None:
        pass
