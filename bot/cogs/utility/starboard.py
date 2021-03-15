import textwrap
import typing as t

import discord
from discord.ext.commands import (Cog, Context, TextChannelConverter, group,
                                  guild_only, has_permissions)

from bot import Bot
from bot.databases.starboard import Starboard as StarboardDB
from bot.utils.utils import confirmation


class Starboard(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    async def emoji_string(emoji: str, guild: discord.Guild) -> str:
        try:
            emoji_string = str(
                discord.utils.get(guild.emojis, id=int(emoji)
                                  ) or "Deleted Emoji"
            )
        except Exception:
            emoji_string = emoji

        return emoji_string

    @Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        guild_id = payload.guild_id

        if guild_id is None:
            return

        channel_id = payload.channel_id
        message_id = payload.message_id
        user_id = payload.user_id

        emoji = payload.emoji
        emoji_name = str(emoji.id) if emoji.id is not None else emoji.name

        row = await StarboardDB.get_config(self.bot.database, guild_id)

        if not row:
            return

        db_emoji = str(row["sb_emoji"])

        if emoji_name != db_emoji:
            return

    @group(invoke_without_command=True)
    @guild_only()
    @has_permissions(manage_channels=True, manage_messages=True)
    async def starboard(self, ctx: Context) -> None:
        """Commands for the starboard control and management."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if not row:
            row = {
                "channel_id": None,
                "emoji": "star",
                "required_stars": 3,
                "required_to_lose": 0,
                "bots_in_sb": False,
                "locked": False,
                "on_edit": True,
                "on_delete": False,
            }

        await ctx.send(
            embed=discord.Embed(
                title="Starboard settings configuration",
                description=textwrap.dedent(
                    f"""
                    • Channel: {
                        f"<#{row['channel_id']}>" if row["channel_id"] is not None else "No channel configured!"
                        }
                    • Emoji: {await self.emoji_string(row["sb_emoji"], ctx.guild)}
                    • Required stars: **`{row["required_stars"]}`**
                    • Stars to lose: **`{row["required_to_lose"]}`**
                    • Bots in starboard: **`{row["bots_in_sb"]}`**
                    • Starboard locked: **`{row["locked"]}`**
                    • Edit when the user edits: **`{row["on_edit"]}`**
                    • Delete when the user deletes: **`{row["on_delete"]}`**
                    """
                ),
                color=discord.Color.blue(),
            )
        )

    @starboard.command()
    async def add(self, ctx: Context, channel: TextChannelConverter) -> None:
        """Register a channel as a starboard."""
        await StarboardDB.set_starboard_channel(
            self.bot.database, ctx.guild.id, channel.id
        )
        await ctx.send(f"Created starboard {channel.mention}")

    @starboard.command()
    async def remove(self, ctx: Context) -> None:
        """Remove a channel from being a starboard."""
        confirm = await confirmation(
            ctx,
            "Do you really want to delete the starboard channel? The messages will be lost forever.",
            "Delete starboard channel",
            discord.Color.gold(),
        )

        if confirm:
            await StarboardDB.delete_starboard_channel(self.bot.database, ctx.guild.id)
            await ctx.send("Deleted starboard from this server.")

    @starboard.command()
    async def set_required_stars(self, ctx: Context, stars: int) -> None:
        """Set the required stars for a message to be starboard archived."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if stars <= row["required_to_lose"]:
            print(row["required_stars"], row["required_to_lose"])
            await ctx.send(
                "The number of stars cannot be equal to or smaller than required to lose."
            )
            return

        await StarboardDB.set_required_stars(self.bot.database, ctx.guild.id, stars)
        await ctx.send(f"Set required stars to {stars}!")

    @starboard.command()
    async def set_required_to_lose(self, ctx: Context, stars: int) -> None:
        """Set the number of stars to lose the starboard message."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if row["required_stars"] <= stars:
            await ctx.send(
                "The number of stars cannot be equal to or smaller than stars required."
            )
            return

        await StarboardDB.set_required_to_lose(self.bot.database, ctx.guild.id, stars)
        await ctx.send(f"Set required to lose to {stars}!")

    @starboard.command()
    async def set_on_edit(self, ctx: Context) -> None:
        """Edit the starboard on actual message edit."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if not row["on_edit"]:
            await StarboardDB.set_on_edit(self.bot.database, ctx.guild.id, True)
            await ctx.send("Messages will be edited when the user edits.")
        else:
            await StarboardDB.set_on_edit(self.bot.database, ctx.guild.id, False)
            await ctx.send("Messages will not be edited when the user edits.")

    @starboard.command()
    async def set_on_delete(self, ctx: Context) -> None:
        """Delete the starboard message if original message is deleted."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if not row["on_delete"]:
            await StarboardDB.set_on_delete(self.bot.database, ctx.guild.id, True)
            await ctx.send("Messages will be deleted when the user deletes.")
        else:
            await StarboardDB.set_on_delete(self.bot.database, ctx.guild.id, False)
            await ctx.send("Messages will not be deleted when the user deletes.")

    @starboard.command()
    async def starboard_bot_messages(self, ctx: Context) -> None:
        """Can bot messages be added to starboard."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if not row["bots_in_sb"]:
            await StarboardDB.set_bots_in_sb(self.bot.database, ctx.guild.id, True)
            await ctx.send("Bot messages will be added to starboard.")
        else:
            await StarboardDB.set_bots_in_sb(self.bot.database, ctx.guild.id, False)
            await ctx.send("Bot messages won't be added to starboard anymore.")

    @starboard.command()
    async def emoji(self, ctx: Context, emoji: t.Union[str, discord.Emoji]) -> None:
        """Set the required stars for a message to be starboard archived."""
        emoji_name = str(emoji.id) if isinstance(
            emoji, discord.Emoji) else emoji

        await StarboardDB.set_sb_emoji(self.bot.database, ctx.guild.id, emoji_name)
        await ctx.send(f"Set {emoji} as the starboard emoji")
