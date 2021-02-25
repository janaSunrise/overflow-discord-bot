import io
import textwrap
import urllib

import aiohttp
import discord
from discord.ext.commands import (BadArgument, Cog, Context, clean_content,
                                  command)

from bot import Bot, config
from bot.utils.pages import EmbedPages
from bot.utils.utils import create_urban_embed_list


class Study(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.headers = {"user-agent": "overflow-discord-bot"}
        self.footer_icon = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Wikimedia-logo.png"
            "/600px-Wikimedia-logo.png"
        )

    @command()
    async def urban(self, ctx: Context, *, word: str) -> None:
        """Search the urban dictionary for a term."""
        url = "http://api.urbandictionary.com/v0/define"
        async with self.bot.session.get(url, params={"term": word}) as resp:
            if resp.status != 200:
                embed = discord.Embed(
                    title="Response Error occurred!",
                    description=textwrap.dedent(
                        f"""
                        Status Code: {resp.status}
                        Reason: {resp.reason}
                        """
                    ),
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)
                return

            json = await resp.json()
            data = json.get("list", [])
            if not data:
                embed = discord.Embed(
                    description="No results found, sorry.", color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        await EmbedPages((await create_urban_embed_list(data))).start(ctx)

    @command()
    async def calc(self, ctx: Context, *, equation: str) -> None:
        """Calculate an equation."""
        params = {"expr": equation}
        url = "http://api.mathjs.org/v4/"
        async with self.bot.session.get(url, params=params) as resp:
            r = await resp.text()
            try:
                response = config.RESPONSES[resp.status]
            except KeyError:
                response = "Invalid Equation"
                emb = discord.Embed(
                    title="ERROR!",
                    description="❌ Invalid Equation Specified, Please Recheck the Equation",
                    color=discord.Color.red(),
                )
                emb.set_footer(text=f"Invoked by {str(ctx.message.author)}")
                await ctx.send(embed=emb)

        if response is True:
            embed = discord.Embed(title="Equation Results")
            embed.add_field(name="**❯❯ Question**",
                            value=equation, inline=False)
            embed.add_field(name="**❯❯ Result**", value=r, inline=False)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")
            await ctx.send(embed=embed)

    @command(aliases=["wiki"])
    async def wikipedia(self, ctx: Context, *, query: str) -> None:
        """Get information from Wikipedia."""
        payload = {
            "action": "query",
            "titles": query.replace(" ", "_"),
            "format": "json",
            "formatversion": "2",
            "prop": "extracts",
            "exintro": "1",
            "redirects": "1",
            "explaintext": "1",
        }

        conn = aiohttp.TCPConnector()

        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(
                self.base_url, params=payload, headers=self.headers
            ) as res:
                result = await res.json()

            await session.close()

        try:
            # Get the last page. Usually this is the only page.
            for page in result["query"]["pages"]:
                title = page["title"]
                description = page["extract"].strip().replace("\n", "\n\n")
                url = "https://en.wikipedia.org/wiki/{}".format(
                    title.replace(" ", "_"))

            if len(description) > 1500:
                description = description[:1500].strip()
                description += f"... [(read more)]({url})"

            embed = discord.Embed(
                title=f"Wikipedia: {title}",
                description="\u2063\n{}\n\u2063".format(description),
                color=discord.Color.blue(),
                url=url,
            )
            embed.set_footer(text="Wikipedia", icon_url=self.footer_icon)
            await ctx.send(embed=embed)

        except KeyError:
            await ctx.send(
                embed=discord.Embed(
                    description=f"I'm sorry, I couldn't find \"{query}\" on Wikipedia",
                    color=discord.Color.red(),
                )
            )

    @command()
    async def latex(self, ctx: Context, *, equation: str) -> None:
        LATEX_URL = "https://latex.codecogs.com/gif.download?%5Cbg_white%20%5Clarge%20"

        cleaned = await clean_content().convert(ctx, equation)
        raw_eq = r"{}".format(cleaned)
        url_eq = urllib.parse.quote(raw_eq)

        async with aiohttp.ClientSession() as session:
            async with session.get(LATEX_URL + url_eq) as result:
                img = await result.read()

        if not 200 <= result.status < 300:
            raise BadArgument(
                f"```{equation}``` is not a valid expression or equation")

        output_img = discord.File(fp=io.BytesIO(img), filename="latex_eq.png")
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(
            name=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        embed.set_image(url="attachment://latex_eq.png")
        return await ctx.channel.send(file=output_img, embed=embed)
