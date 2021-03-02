import textwrap

import discord
from discord.ext.commands import Cog, Context, group, guild_only, has_permissions

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

        if ctx.author != ctx.guild.owner or await ctx.guild.fetch_member(ctx.guild.owner_id):
            await ctx.send("This command is available to guild owners only.")
            return

        if mode in ("yes", "enable"):
            await SwearFilterDB.set_notification(self.bot.database, ctx.guild.id, True)
            await ctx.send("Automatic swear notification enabled!")
        else:
            await SwearFilterDB.set_notification(self.bot.database, ctx.guild.id, False)
            await ctx.send("Automatic swear notification disabled.")

    @swear_filter.group(aliases=["word"], invoke_without_command=True)
    async def words(self, ctx: Context) -> None:
        """Configuration for the swear words."""
        await ctx.send_help(ctx.command)

    @words.command()
    async def add(self, ctx: Context, word: str = None) -> None:
        """Add a word to the swear filter list."""
        if not word:
            await ctx.send(":x: Specify a word to be added to the swear filter list.")

        row = await SwearFilterDB.get_config(self.bot.database, ctx.guild.id)
        word = word.lower()

        words = []
        if row is not None:
            words += row["words"]

        if word not in words:
            words.append(word)
            await SwearFilterDB.set_words(self.bot.database, ctx.guild.id, words)
            await ctx.send(f"`{word}` successfully added to the swear filter list.")
        else:
            await ctx.send("Word is already in the swear filter list.")

    @words.command()
    async def remove(self, ctx: Context, word: str = None) -> None:
        """Remove a word from the swear filter list."""
        if not word:
            await ctx.send(":x: Specify a word to be removed from the swear filter list.")

        row = await SwearFilterDB.get_config(self.bot.database, ctx.guild.id)
        word = word.lower()

        words = []
        if row is not None:
            words += row["words"]

        if word in words:
            words.remove(word)
            await SwearFilterDB.set_words(self.bot.database, ctx.guild.id, words)
            await ctx.send(f"`{word}` successfully removed the swear filter list.")
        else:
            await ctx.send("Word is not in the swear filter list.")

    @words.command()
    async def clear(self, ctx: Context) -> None:
        """Remove all the swear words configured."""
        await SwearFilterDB.set_words(self.bot.database, ctx.guild.id, [])
        await ctx.send("Swear filter wordlist cleared.")
