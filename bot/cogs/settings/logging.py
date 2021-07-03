import textwrap

import discord
from discord.ext.commands import (
    Cog,
    Context,
    TextChannelConverter,
    group,
    has_permissions,
)

from bot import Bot
from bot.databases.logging import Logging


class LoggingSettings(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(
        invoke_without_command=True,
        aliases=["log-config", "logging", "logchannel", "log"],
    )
    @has_permissions(manage_channels=True)
    async def logging_config(self, ctx: Context) -> None:
        row = await Logging.get_config(self.bot.database, ctx.guild.id)

        if row is None:
            row = {
                "server_log": None,
                "mod_log": None,
                "message_log": None,
                "member_log": None,
                "join_log": None,
                "voice_log": None,
            }

        await ctx.send(
            embed=discord.Embed(
                title="Logging channel configuration",
                description=textwrap.dedent(
                    f"""
                    ❯ Server log: {row["server_log"]}
                    ❯ Mod log: {row["mod_log"]}
                    ❯ Message log: {row["message_log"]}
                    ❯ Member log: {row["member_log"]}
                    ❯ Join log: {row["join_log"]}
                    ❯ Voice log: {row["voice_log"]}
                    """
                ),
                color=discord.Color.blue(),
            )
        )

    @logging_config.command()
    async def server(self, ctx: Context, channel: TextChannelConverter = None) -> None:
        if not channel:
            await ctx.send(
                ":x: Specify a channel to configure as the server log channel."
            )

        await Logging.set_log_channel(
            self.bot.database, "server_log", ctx.guild.id, channel.id
        )
        await ctx.send("Successfully configured the server log channel.")

    @logging_config.command()
    async def mod(self, ctx: Context, channel: TextChannelConverter = None) -> None:
        if not channel:
            await ctx.send(":x: Specify a channel to configure as the mod log channel.")

        await Logging.set_log_channel(
            self.bot.database, "mod_log", ctx.guild.id, channel.id
        )
        await ctx.send("Successfully configured the mod log channel.")

    @logging_config.command()
    async def message(self, ctx: Context, channel: TextChannelConverter = None) -> None:
        if not channel:
            await ctx.send(
                ":x: Specify a channel to configure as the message log channel."
            )

        await Logging.set_log_channel(
            self.bot.database, "message_log", ctx.guild.id, channel.id
        )
        await ctx.send("Successfully configured the message log channel.")

    @logging_config.command()
    async def member(self, ctx: Context, channel: TextChannelConverter = None) -> None:
        if not channel:
            await ctx.send(
                ":x: Specify a channel to configure as the member log channel."
            )

        await Logging.set_log_channel(
            self.bot.database, "member_log", ctx.guild.id, channel.id
        )
        await ctx.send("Successfully configured the member log channel.")

    @logging_config.command()
    async def join(self, ctx: Context, channel: TextChannelConverter = None) -> None:
        if not channel:
            await ctx.send(
                ":x: Specify a channel to configure as the join log channel."
            )

        await Logging.set_log_channel(
            self.bot.database, "join_log", ctx.guild.id, channel.id
        )
        await ctx.send("Successfully configured the join log channel.")

    @logging_config.command()
    async def voice(self, ctx: Context, channel: TextChannelConverter = None) -> None:
        if not channel:
            await ctx.send(
                ":x: Specify a channel to configure as the voice log channel."
            )

        await Logging.set_log_channel(
            self.bot.database, "voice_log", ctx.guild.id, channel.id
        )
        await ctx.send("Successfully configured the voice log channel.")
