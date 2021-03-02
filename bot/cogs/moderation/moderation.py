import asyncio
import typing as t
from contextlib import suppress
from datetime import datetime
from textwrap import dedent

import discord
from discord.ext.commands import (Cog, Context, Greedy, MemberConverter,
                                  NoPrivateMessage, RoleConverter, command,
                                  has_permissions)

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
            ctx, action="ban", user=member, reason=reason, color=discord.Color.gold()
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
            ctx, action="ban", user=member, reason=reason, color=discord.Color.gold()
        )
        embed.timestamp = datetime.utcnow()
        embed.set_thumbnail(url=member.avatar_url_as(format="png", size=256))

        await ctx.send(embed=embed)
        await member.ban(reason=reason)
        await member.unban(reason=reason)

    @command()
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
            embed=discord.Embed(description=description,
                                color=discord.Color.green()),
        )
        await asyncio.sleep(4)
        await message.delete()

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
