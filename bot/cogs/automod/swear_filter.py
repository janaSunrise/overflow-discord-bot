import textwrap

import discord
from discord.ext.commands import (Cog, Context, group, guild_only,
                                  has_permissions)

from bot import Bot
from bot.databases.swear_filter import SwearFilter as SwearFilterDB


class SwearFilter(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(aliases=["swear-filter"], invoke_without_command=True)
    @guild_only()
    @has_permissions(ban_members=True)
    async def swear_filter(self, ctx: Context) -> None:
        """Define the group for the profanity filter, aka swear detection."""
        row = await SwearFilterDB.get_config(self.bot.database, ctx.guild.id)

        if not row:
            row = {
                "manual_on": False,
                "autoswear": False,
                "notification": False,
                "words": [],
            }

        await ctx.send(
            embed=discord.Embed(
                title="Role settings configuration",
                description=textwrap.dedent(
                    f"""
                    • Manual mode: {row["manual_on"]}
                    • Auto swear detection: {row["autoswear"]} 
                    • Owner notification: {row["notification"]}
                    • Word list: `{row["words"]}`
                    """
                ),
                color=discord.Color.blue(),
            )
        )

    @swear_filter.command()
    async def mode(self, ctx: Context, mode: str) -> None:
        """
        Configure the mode for the swear filter, if to enable or disable it.

        Modes available:
        - `yes` / `enable` to enable it.
        - `no` / `disable` to disable it.
        """
        mode = mode.lower()

        if mode not in ("yes", "no", "enable", "disable"):
            await ctx.send(
                "Invalid mode! Possible modes are `yes`, `no`, `enable`, `disable`. Check the help for further notice."
            )
            return

        if mode in ("yes", "enable"):
            await SwearFilterDB.set_filter_mode(self.bot.database, ctx.guild.id, True)
            await ctx.send("Swear filter enabled!")
        else:
            await SwearFilterDB.set_filter_mode(self.bot.database, ctx.guild.id, False)
            await ctx.send("Swear filter disabled.")

    @swear_filter.command()
    async def auto(self, ctx: Context, mode: str) -> None:
        """
        Automatic mode to catch filters, without adding words explicitly.

        Modes available:
        - `yes` / `enable` to enable it.
        - `no` / `disable` to disable it.
        """
        mode = mode.lower()

        if mode not in ("yes", "no", "enable", "disable"):
            await ctx.send(
                "Invalid mode! Possible modes are `yes`, `no`, `enable`, `disable`. Check the help for further notice."
            )
            return

        if mode in ("yes", "enable"):
            await SwearFilterDB.set_auto_mode(self.bot.database, ctx.guild.id, True)
            await ctx.send("Automatic swear filter enabled!")
        else:
            await SwearFilterDB.set_auto_mode(self.bot.database, ctx.guild.id, False)
            await ctx.send("Automatic swear filter disabled.")

    @swear_filter.command()
    async def notification(self, ctx: Context, mode: str) -> None:
        """
        Command to notify owner if any user swears, if subscribed.

        Modes available:
        - `yes` / `enable` to enable it.
        - `no` / `disable` to disable it.
        """
        mode = mode.lower()

        if mode not in ("yes", "no", "enable", "disable"):
            await ctx.send(
                "Invalid mode! Possible modes are `yes`, `no`, `enable`, `disable`. Check the help for further notice."
            )
            return

        if ctx.author != ctx.guild.owner or await ctx.guild.fetch_member(
            ctx.guild.owner_id
        ):
            await ctx.send("This command is available to guild owners only.")
            return

        if mode in ("yes", "enable"):
            await SwearFilterDB.set_notification(self.bot.database, ctx.guild.id, True)
            await ctx.send("Automatic swear notification enabled!")
        else:
            await SwearFilterDB.set_notification(self.bot.database, ctx.guild.id, False)
            await ctx.send("Automatic swear notification disabled.")
