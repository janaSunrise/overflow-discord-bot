import re
import textwrap
import typing as t
import weakref

import discord
from discord.ext import tasks
from discord.ext.commands import (CheckFailure, Cog, Context,
                                  TextChannelConverter, group, guild_only,
                                  has_permissions)

from bot import Bot
from bot.databases.starboard import Starboard as StarboardDB
from bot.databases.starboard import StarboardMessage as SBMessageDB
from bot.utils.utils import confirmation


class StarError(CheckFailure):
    pass


class Starboard(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        # cache message objects to save Discord some HTTP requests.
        self._message_cache = {}
        self.clean_message_cache.start()

        # if it's in this set,
        self._about_to_be_deleted = set()

        self._locks = weakref.WeakValueDictionary()
        self.spoilers = re.compile(r"\|\|(.+?)\|\|")

    def cog_unload(self):
        self.clean_message_cache.cancel()

    @tasks.loop(hours=1.0)
    async def clean_message_cache(self):
        self._message_cache.clear()

    @staticmethod
    def star_emoji(stars: int) -> str:
        if 5 > stars >= 0:
            return "\N{WHITE MEDIUM STAR}"
        elif 10 > stars >= 5:
            return "\N{GLOWING STAR}"
        elif 25 > stars >= 10:
            return "\N{DIZZY SYMBOL}"
        else:
            return "\N{SPARKLES}"

    @staticmethod
    def star_gradient_colour(stars: int) -> int:
        p = stars / 13
        if p > 1.0:
            p = 1.0

        red = 255
        green = int((194 * p) + (253 * (1 - p)))
        blue = int((12 * p) + (247 * (1 - p)))
        return (red << 16) + (green << 8) + blue

    def is_url_spoiler(self, text: str, url: str) -> bool:
        spoilers = self.spoilers.findall(text)

        for spoiler in spoilers:
            if url in spoiler:
                return True
        return False

    def get_emoji_message(self, message: discord.Message, stars: int) -> tuple:
        emoji = self.star_emoji(stars)

        if stars > 1:
            content = f"{emoji} **{stars}** {message.channel.mention} ID: {message.id}"
        else:
            content = f"{emoji} {message.channel.mention} ID: {message.id}"

        embed = discord.Embed(description=message.content)
        if message.embeds:
            data = message.embeds[0]
            if data.type == "image" and not self.is_url_spoiler(
                message.content, data.url
            ):
                embed.set_image(url=data.url)

        if message.attachments:
            file = message.attachments[0]
            spoiler = file.is_spoiler()
            if not spoiler and file.url.lower().endswith(
                ("png", "jpeg", "jpg", "gif", "webp")
            ):
                embed.set_image(url=file.url)
            elif spoiler:
                embed.add_field(
                    name="Attachment",
                    value=f"||[{file.filename}]({file.url})||",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Attachment",
                    value=f"[{file.filename}]({file.url})",
                    inline=False,
                )

        embed.add_field(
            name="Original", value=f"[Jump!]({message.jump_url})", inline=False
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar_url_as(format="png"),
        )
        embed.timestamp = message.created_at
        embed.colour = self.star_gradient_colour(stars)
        return content, embed

    async def get_message(
        self, channel: discord.TextChannel, message_id: int
    ) -> t.Optional[discord.Message]:
        try:
            return self._message_cache[message_id]
        except KeyError:
            try:
                o = discord.Object(id=message_id + 1)

                def pred(m):
                    return m.id == message_id

                msg = await channel.history(limit=1, before=o).next()

                if msg.id != message_id:
                    return None

                self._message_cache[message_id] = msg
                return msg
            except Exception:
                return None

    async def reaction_action(self, fmt: str, payload: t.Any) -> None:
        if str(payload.emoji) != "\N{WHITE MEDIUM STAR}":
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        channel = guild.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        method = getattr(self, f"{fmt}_message")

        user = payload.member or (
            await self.bot.get_or_fetch_member(guild, payload.user_id)
        )
        if user is None or user.bot:
            return

        try:
            await method(channel, payload.message_id, payload.user_id, verify=True)
        except StarError:
            pass

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.TextChannel) -> None:
        if not isinstance(channel, discord.TextChannel):
            return

        starboard = await StarboardDB.get_config(self.bot.database, channel.guild.id)
        if starboard["channel_id"] is None or starboard["channel_id"] != channel.id:
            return

        await StarboardDB.delete_starboard_channel(self.bot.database, channel.guild.id)

    @Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.raw_models.RawReactionActionEvent
    ) -> None:
        await self.reaction_action("star", payload)

    @Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.raw_models.RawReactionClearEvent
    ) -> None:
        await self.reaction_action("unstar", payload)

    @Cog.listener()
    async def on_raw_message_delete(
        self, payload: discord.raw_models.RawMessageDeleteEvent
    ) -> None:
        if payload.message_id in self._about_to_be_deleted:
            self._about_to_be_deleted.discard(payload.message_id)
            return

        starboard = await StarboardDB.get_config(self.bot.database, payload.guild_id)
        if (
            starboard["channel_id"] is None
            or starboard["channel_id"] != payload.channel_id
        ):
            return

        await SBMessageDB.delete_starboard_message(
            self.bot.database, payload.message_id
        )

    @Cog.listener()
    async def on_raw_bulk_message_delete(
        self, payload: discord.raw_models.RawBulkMessageDeleteEvent
    ) -> None:
        if payload.message_ids <= self._about_to_be_deleted:
            self._about_to_be_deleted.difference_update(payload.message_ids)
            return

        starboard = await StarboardDB.get_config(self.bot.database, payload.guild_id)
        if (
            starboard["channel_id"] is None
            or starboard["channel_id"] != payload.channel_id
        ):
            return

        await SBMessageDB.delete_starboard_message(
            self.bot.database, list(payload.message_ids)
        )

    @Cog.listener()
    async def on_raw_reaction_clear(
        self, payload: discord.raw_models.RawReactionClearEvent
    ) -> None:
        channel = self.bot.get_channel(payload.channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            return

        starboard = await StarboardDB.get_config(self.bot.database, payload.guild_id)
        if starboard["channel_id"] is None:
            return

        bot_message_id = (
            await SBMessageDB.delete_starboard_id(self.bot.database, payload.message_id)
        )["bot_message_id"]

        if bot_message_id is None:
            return

        bot_message_id = bot_message_id[0]
        msg = await self.get_message(starboard["channel_id"], bot_message_id)
        if msg is not None:
            await msg.delete()

    @group(invoke_without_command=True)
    @guild_only()
    @has_permissions(manage_channels=True, manage_messages=True)
    async def starboard(self, ctx: Context) -> None:
        """Commands for the starboard control and management."""
        row = await StarboardDB.get_config(self.bot.database, ctx.guild.id)

        if not row:
            await ctx.send("⚠️Starboard channel not configured!")
            return

        await ctx.send(
            embed=discord.Embed(
                title="Starboard settings configuration",
                description=textwrap.dedent(
                    f"""
                    • Channel: {f"<#{row['channel_id']}>"}
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
