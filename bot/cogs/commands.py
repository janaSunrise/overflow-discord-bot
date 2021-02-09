import textwrap
import time
import re

import discord
from discord.ext import commands

from bot import Bot


class Commands(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Show bot ping."""
        start = time.perf_counter()
        embed = discord.Embed(title="Info", description="Pong!", color=discord.Color.blurple())
        message = await ctx.send(embed=embed)
        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        discord_start = time.monotonic()
        async with self.bot.session.get("https://discord.com/") as resp:
            if resp.status == 200:
                discord_end = time.monotonic()
                discord_ms = f"{round((discord_end - discord_start) * 1000)}ms"
            else:
                discord_ms = "fucking dead"

        desc = textwrap.dedent(
            f"""
                :ping_pong: Pong!
                Bot ping: **{duration}ms**
                Discord Server Ping: **{discord_ms}**
                Speed Ping: **{round(self.bot.latency * 1000)}ms**
                """
        )

        embed = discord.Embed(title="Info", description=desc, color=discord.Color.blurple())
        await message.edit(embed=embed)

    @commands.command()
    async def paste(self, ctx: commands.Context, *, text: str) -> None:
        """Creates a Paste out of the text specified."""
        async with self.bot.session.post("https://hasteb.in/documents", data=self._clean_code(text)) as resp:
            key = (await resp.json())['key']
            file_paste = 'https://www.hasteb.in/' + key

            await ctx.send(
                embed=discord.Embed(title="File pastes", description=file_paste, color=discord.Color.blue())
            )

    @staticmethod
    def _clean_code(code: str) -> str:
        codeblock_match = re.fullmatch(r"\`\`\`(.*\n)?((?:[^\`]*\n*)+)\`\`\`", code)
        if codeblock_match:
            lang = codeblock_match.group(1)
            code = codeblock_match.group(2)
            ret = lang if not code else code
            if ret[-1] == "\n":
                ret = ret[:-1]
            return ret

        simple_match = re.fullmatch(r"\`(.*\n*)\`", code)
        if simple_match:
            return simple_match.group(1)

        return code

    @commands.cooldown(1, 10, commands.BucketType.member)
    async def shorten(self, ctx: commands.Context, *, link: str) -> None:
        """Make a link shorter using the tinyurl api."""
        if not link.startswith("https://"):
            await ctx.send(f"Invalid link: `{link}`. Enter a valid URL.")
            return

        url = link.strip("<>")
        url = f"http://tinyurl.com/api-create.php?url={url}"

        async with self.bot.session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("Error retrieving shortened URL, please try again in a minute.")
                return
            shortened_link = await resp.text()

        embed = discord.Embed(color=discord.Color.blurple())
        embed.add_field(name="Original Link", value=link, inline=False)
        embed.add_field(name="Shortened Link", value=shortened_link, inline=False)
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
