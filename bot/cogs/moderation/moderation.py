import asyncio
import typing as t
from contextlib import suppress
from textwrap import dedent

import discord
from discord.ext.commands import (
    Cog,
    Context,
    Greedy,
    NoPrivateMessage,
    command,
    has_permissions
)

from bot import Bot


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
    @has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, amount: int, member: discord.Member = None) -> None:
        """Clear messages from a specific channel. Specify a member to clear his messages only."""
        if not member:
            await ctx.message.channel.purge(limit=amount)
        else:
            await ctx.message.channel.purge(limit=amount, check=lambda msg: msg.author == member)

        description = dedent(f"""
        **Cleared messages!**

        • Count: {amount}
        """)

        description += f"• Member: {member.mention}" if member else ""

        message = await ctx.send(
            f"Hey {ctx.author.mention}!",
            embed=discord.Embed(
                description=description,
                color=discord.Color.green()
            )
        )
        await asyncio.sleep(4)
        await message.delete()

    @command()
    @has_permissions(manage_roles=True)
    async def dm(
            self,
            ctx: Context,
            members: Greedy[t.Union[discord.Member, discord.Role]],
            *,
            text: str = None
    ) -> None:
        """Dm a List of Specified User from Your Guild."""
        embed_data = self.embeds_cog.embeds[ctx.author.id]

        if embed_data.embed.description is None and embed_data.embed.title is None:
            await ctx.send(":x: You need to create an embed using our embed maker before sending it!")
            return

        if text is not None:
            embed_data.embed.description = text

        if not embed_data.embed.footer:
            embed_data.embed.set_footer(text=f"From {ctx.guild.name}", icon_url=ctx.guild.icon_url)

        for member in members:
            if isinstance(member, discord.Role):
                for mem in member.members:
                    with suppress(discord.Forbidden, discord.HTTPException):
                        await mem.send(embed=embed_data.embed)
            else:
                with suppress(discord.Forbidden, discord.HTTPException):
                    await member.send(embed=embed_data.embed)

            await ctx.message.add_reaction("✅")
