import asyncio
from textwrap import dedent

import discord
from discord.ext import commands

from bot import Bot


class Moderation(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        if ctx.guild:
            return True

        raise commands.NoPrivateMessage

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int, member: discord.Member = None) -> None:
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
