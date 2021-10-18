import asyncio
import re
import typing as t
from collections import Counter
from contextlib import suppress
from datetime import datetime
from textwrap import dedent

import discord
from discord.ext.commands import (
    Cog,
    Context,
    Greedy,
    MemberConverter,
    NoPrivateMessage,
    RoleConverter,
    UserConverter,
    command,
    group,
    guild_only,
    has_permissions,
)

from bot import Bot
from bot.core.converters import ModerationReason
from bot.utils.embeds import moderation_embed


class Moderation(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @property
    def embeds_cog(self) -> discord.Embed:
        """Get currently loaded Embed cog instance."""
        return self.bot.get_cog("Embeds")

    def cog_check(self, ctx: Context):
        if ctx.guild:
            return True

        raise NoPrivateMessage

    @command(aliases=["purge"])
    @has_permissions(manage_messages=True)
    async def clear(
        self, ctx: Context, amount: int, member: MemberConverter = None
    ) -> None:
        """Clear messages from a specific channel. Specify a member to clear his messages only."""
        if not member:
            await ctx.message.channel.purge(limit=amount)
        else:
            await ctx.message.channel.purge(
                limit=amount, check=lambda msg: msg.author == member
            )

        description = dedent(
            f"""
        **Cleared messages!**

        • Count: {amount}
        """
        )

        description += f"• Member: {member.mention}" if member else ""

        message = await ctx.send(
            f"Hey {ctx.author.mention}!",
            embed=discord.Embed(description=description, color=discord.Color.green()),
        )
        await asyncio.sleep(4)
        await message.delete()

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f"Too many messages to search given ({limit}/2000)")

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(
                limit=limit, before=before, after=after, check=predicate
            )
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"• **{name}**: {count}" for name, count in spammers)

        to_send = "\n".join(messages)

        if len(to_send) > 2000:
            await ctx.send(f"Successfully removed {deleted} messages.", delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @group(aliases=["advanced-purge", "advanced-clear", "advanced-clean"])
    @guild_only()
    @has_permissions(manage_messages=True)
    async def advanced_clear(self, ctx):
        """Advanced message removal service with various categories, like images embeds, certain text and such."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @advanced_clear.command()
    async def embeds(self, ctx: Context, search: int = 100) -> None:
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @advanced_clear.command()
    async def files(self, ctx: Context, search: int = 100) -> None:
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @advanced_clear.command()
    async def images(self, ctx: Context, search: int = 100) -> None:
        """Removes messages that have embeds or attachments."""
        await self.do_removal(
            ctx, search, lambda e: len(e.embeds) or len(e.attachments)
        )

    @advanced_clear.command()
    async def user(
        self, ctx: Context, member: discord.Member, search: int = 100
    ) -> None:
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @advanced_clear.command()
    async def contains(self, ctx: Context, *, substr: str) -> None:
        """Removes all messages containing a substring.Must be atleast 3 characters long."""
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @advanced_clear.command(name="bot", aliases=["bots"])
    async def _bot(self, ctx: Context, prefix: str = None, search: int = 100) -> None:
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m: t.Any) -> t.Any:
            return (m.webhook_id is None and m.author.bot) or (
                prefix and m.content.startswith(prefix)
            )

        await self.do_removal(ctx, search, predicate)

    @advanced_clear.command(name="emoji", aliases=["emojis"])
    async def _emoji(self, ctx: Context, search: int = 100) -> None:
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @advanced_clear.command(name="reactions")
    async def _reactions(self, ctx: Context, search: int = 100) -> None:
        """Removes all reactions from messages that have them."""
        if search > 2000:
            await ctx.send(f"Too many messages to search for ({search} / 2000)")
            return

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f"Successfully removed {total_reactions} reactions.")

    @command()
    @has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: Context,
        member: MemberConverter,
        *,
        reason: ModerationReason = "No reason specified.",
    ) -> None:
        """Kick a member from your server."""
        if not isinstance(member, discord.Member):
            await ctx.send(
                embed=discord.Embed(
                    description=dedent(
                        f"""
                    You cannot kick this member!

                    {member.mention} [**`{member.id}`**] isn't a member of this server. You can only kick members in this
                    server.
                    """
                    )
                )
            )
            return

        embed = moderation_embed(
            ctx, action="kick", user=member, reason=reason, color=discord.Color.gold()
        )
        embed.timestamp = datetime.utcnow()
        embed.set_thumbnail(url=member.avatar_url_as(format="png", size=256))

        await ctx.send(embed=embed)
        await member.kick(reason=reason)

    @command()
    @has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: Context,
        member: MemberConverter,
        *,
        reason: ModerationReason = "No reason specified.",
    ) -> None:
        """Ban a member from your server."""
        embed = moderation_embed(
            ctx, action="bann", user=member, reason=reason, color=discord.Color.gold()
        )
        embed.timestamp = datetime.utcnow()
        embed.set_thumbnail(url=member.avatar_url_as(format="png", size=256))

        await ctx.send(embed=embed)
        await member.ban(reason=reason)

    @command()
    @has_permissions(ban_members=True)
    async def softban(
        self,
        ctx: Context,
        member: MemberConverter,
        *,
        reason: ModerationReason = "No reason specified.",
    ) -> None:
        """Ban and unban a member from your server."""
        if "softban" not in reason:
            reason = "[SOFTBANNED] " + reason

        embed = moderation_embed(
            ctx, action="bann", user=member, reason=reason, color=discord.Color.gold()
        )
        embed.timestamp = datetime.utcnow()
        embed.set_thumbnail(url=member.avatar_url_as(format="png", size=256))

        await ctx.send(embed=embed)
        await member.ban(reason=reason)
        await member.unban(reason=reason)

    @command()
    @has_permissions(ban_members=True)
    async def unban(
        self, ctx: Context, *, user: UserConverter, reason: str = "Not specified."
    ) -> None:
        try:
            await ctx.guild.unban(user)

            embed = moderation_embed(
                ctx,
                action="unbann",
                user=user,
                reason=reason,
                color=discord.Color.gold(),
            )
            embed.timestamp = datetime.utcnow()
            embed.set_thumbnail(url=user.avatar_url_as(format="png", size=256))
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                title="Ban not Found!",
                description=dedent(
                    f"""
                    There are no active bans on discord for {user.mention}.
                    He isn't banned here.
                    """
                ),
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

    @command()
    @has_permissions(kick_members=True)
    async def restrict(self, ctx: Context, member: MemberConverter = None) -> None:
        """Restrict a certain member talking in the current channel."""
        if not member:
            await ctx.send(
                "❌ Please specify an user to restrict talking in this channel."
            )

        await ctx.channel.set_permissions(
            member,
            send_messages=False,
            reason=f"Restrict {member.id} from talking. | Requested by {ctx.author}.",
        )
        await ctx.message.add_reaction("✅")

    @command()
    @has_permissions(kick_members=True)
    async def unrestrict(self, ctx: Context, member: MemberConverter = None) -> None:
        """Restrict a certain member talking in the current channel."""
        if not member:
            await ctx.send(
                "❌ Please specify an user to unrestrict talking in this channel."
            )

        await ctx.channel.set_permissions(
            member,
            send_messages=None,
            reason=f"Un-restrict {member.id} from talking. | Requested by {ctx.author}.",
        )
        await ctx.message.add_reaction("✅")

    @command()
    @has_permissions(manage_roles=True)
    async def dm(
        self,
        ctx: Context,
        members: Greedy[t.Union[MemberConverter, RoleConverter]],
        *,
        text: str = None,
    ) -> None:
        """DM a list of specified users in your server."""
        embed_data = self.embeds_cog.embeds[ctx.author.id]

        if embed_data.embed.description is None and embed_data.embed.title is None:
            await ctx.send(
                "❌ You need to create an embed using our embed maker before sending it!"
            )
            return

        if text is not None:
            embed_data.embed.description = text

        if not embed_data.embed.footer:
            embed_data.embed.set_footer(
                text=f"From {ctx.guild.name}", icon_url=ctx.guild.icon_url
            )

        for member in members:
            if isinstance(member, discord.Role):
                for mem in member.members:
                    with suppress(discord.Forbidden, discord.HTTPException):
                        await mem.send(embed=embed_data.embed)
            else:
                with suppress(discord.Forbidden, discord.HTTPException):
                    await member.send(embed=embed_data.embed)

            await ctx.message.add_reaction("✅")
