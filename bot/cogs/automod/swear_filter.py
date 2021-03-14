import textwrap

import discord
from discord.ext.commands import (
    Cog, Context, group, guild_only,
    has_permissions
)

from bot import Bot, config
from bot.databases.swear_filter import SwearFilter as SwearFilterDB


class SwearFilter(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    def get_human_readable_word(expression: bool) -> str:
        if expression:
            return "Enabled"
        return "Disabled"

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
                title="Swear filter settings configuration",
                description=textwrap.dedent(
                    f"""
                    • Manual mode: {SwearFilter.get_human_readable_word(row["manual_on"])}
                    • Auto swear detection: {SwearFilter.get_human_readable_word(row["autoswear"])}
                    • Owner notification: {SwearFilter.get_human_readable_word(row["notification"])}
                    • Word list: `{row["words"]}`
                    """
                ),
                color=discord.Color.blue(),
            )
        )

    @swear_filter.command()
    async def mode(self, ctx: Context) -> None:
        """Configure the mode for the swear filter, if to enable or disable it."""
        row = await SwearFilterDB.get_config(self.bot.database, ctx.guild.id)

        if not row["manual_on"]:
            await SwearFilterDB.set_filter_mode(self.bot.database, ctx.guild.id, True)
            await ctx.send("Swear filter enabled!")
        else:
            await SwearFilterDB.set_filter_mode(self.bot.database, ctx.guild.id, False)
            await ctx.send("Swear filter disabled.")

    @swear_filter.command()
    async def auto(self, ctx: Context) -> None:
        """Automatic mode to catch filters, without adding words explicitly."""
        row = await SwearFilterDB.get_config(self.bot.database, ctx.guild.id)

        if not row["autoswear"]:
            await SwearFilterDB.set_auto_mode(self.bot.database, ctx.guild.id, True)
            await ctx.send("Automatic swear filter enabled!")
        else:
            await SwearFilterDB.set_auto_mode(self.bot.database, ctx.guild.id, False)
            await ctx.send("Automatic swear filter disabled.")

    @swear_filter.command()
    async def notification(self, ctx: Context) -> None:
        """Command to notify owner if any user swears, if subscribed."""
        row = await SwearFilterDB.get_config(self.bot.database, ctx.guild.id)

        if ctx.author.id != ctx.guild.owner.id:
            await ctx.send("This command is available to guild owners only.")
            return

        if not row["notification"]:
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
            await ctx.send(
                ":x: Specify a word to be removed from the swear filter list."
            )

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

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not message.guild:
            return

        if message.author.guild_permissions.administrator:
            return

        if message.channel.is_nsfw() or message.author.guild_permissions.manage_roles:
            return

        status = await SwearFilterDB.get_config(self.bot.database, message.guild.id)

        if not status:
            return

        owner = message.guild.owner or await message.guild.fetch_member(
            message.guild.owner_id
        )

        if status["autoswear"]:
            if config.filter_words.search(word := message.content.lower()):
                await message.delete()
                await message.channel.send(
                    f"Sorry {message.author.mention}! I removed your message, as it contained a restricted "
                    f"word.",
                    delete_after=10,
                )

                if status["notification"]:
                    await owner.send(
                        f"{message.author} send a forbidden swear word `{word}` in your server"
                        f"`[{message.guild.name}]`"
                    )
                return

        if status["manual_on"]:
            for word in status["words"]:
                if word in message.content.lower().split(r"\s+"):
                    await message.delete()
                    await message.channel.send(
                        f"Sorry {message.author.mention}! I removed your message, as it contained a restricted "
                        f"word.",
                        delete_after=10,
                    )

                    if status["notification"]:
                        await owner.send(
                            f"{message.author} send a forbidden swear word `{word}` in your server"
                            f"`[{message.guild.name}]`"
                        )
