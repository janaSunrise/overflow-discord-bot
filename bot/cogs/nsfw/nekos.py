from random import choice

import aiohttp
from bs4 import BeautifulSoup
from discord import Color, Embed, User
from discord.ext.commands import Bot, Cog, Context, group, guild_only, is_nsfw


class Neko(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @staticmethod
    async def get(url: str, author: User) -> Embed:
        """Gets pictures from Neko API."""
        base = "https://api.nekos.dev/api/v3/"

        async with aiohttp.ClientSession() as session:
            async with session.get(base + url) as response:
                req = await response.json()

        await session.close()

        embed = Embed(color=Color.red())
        embed.title = f"Requested by {author.name}"
        embed.set_image(url=req["data"]["response"]["url"])
        return embed

    @group(invoke_without_command=True)
    async def neko(self, ctx: Context) -> None:
        """Neko Commands Group."""
        await ctx.send_help(ctx.command)

    @neko.command()
    async def nekos(self, ctx: Context) -> None:
        """Gets Neko pics from API."""
        async with ctx.typing():
            sources = ["images/sfw/img/neko", "images/sfw/gif/neko"]
            source = choice(sources)

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        """Gets NSFW Neko pics from API"""
        sources = [
            "images/nsfw/gif/neko",
            "images/nsfw/img/neko_lewd",
            "images/nsfw/img/neko_ero",
        ]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    async def waifu(self, ctx: Context) -> None:
        """Gets Waifu pics from API."""
        async with ctx.typing():
            source = "images/sfw/img/waifu"

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    async def kitsune(self, ctx: Context) -> None:
        """gets Kitsune pics from API."""
        async with ctx.typing():
            source = "images/sfw/img/kitsune"

            embed = await self.get(source, ctx.author)
            await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def lewd(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""

        sources = [
            "images/nsfw/img/classic_lewd",
            "images/nsfw/img/neko_lewd",
            "images/nsfw/img/neko_ero",
        ]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def blowjob(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/blow_job", "images/nsfw/img/blowjob_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def furry(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/yiff", "images/nsfw/img/yiff_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def pussy(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = [
            "images/nsfw/gif/pussy_wank",
            "images/nsfw/gif/pussy",
            "images/nsfw/img/pussy_lewd",
        ]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def feet(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = [
            "images/nsfw/gif/feet",
            "images/nsfw/img/feet_lewd",
            "images/nsfw/img/feet_ero",
        ]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def yuri(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = [
            "images/nsfw/gif/yuri",
            "images/nsfw/img/yuri_lewd",
            "images/nsfw/img/yuri_ero",
        ]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def solo(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/girls_solo", "images/nsfw/img/solo_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def cum(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/gif/cum", "images/nsfw/img/cum_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def cunni(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        source = "images/nsfw/gif/kuni"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def bdsm(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        source = "images/nsfw/img/bdsm_lewd"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def trap(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        sources = ["images/nsfw/img/trap_lewd",
                   "images/nsfw/img/futanari_lewd"]
        source = choice(sources)

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def femdom(self, ctx: Context) -> None:
        """Gets NSFW Images from Neko API."""
        source = "images/nsfw/img/femdom_lewd"

        embed = await self.get(source, ctx.author)
        await ctx.send(embed=embed)

    @neko.command()
    @is_nsfw()
    async def yandere(self, ctx: Context) -> None:
        """Random Image From Yandere"""
        try:
            query = "https://yande.re/post/random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="highres").get("href")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def konachan(self, ctx: Context) -> None:
        """Random Image From Konachan"""
        try:
            query = "https://konachan.com/post/random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="highres").get("href")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def e621(self, ctx: Context) -> None:
        """Random Image From e621"""
        try:
            query = "https://e621.net/post/random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="highres").get("href")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def rule34(self, ctx: Context) -> None:
        """Random Image From rule34"""
        try:
            query = "http://rule34.xxx/index.php?page=post&s=random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def danbooru(self, ctx: Context) -> None:
        """Random Image From Danbooru"""
        try:
            query = "http://danbooru.donmai.us/posts/random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def gelbooru(self, ctx: Context) -> None:
        """Random Image From Gelbooru"""
        try:
            query = "http://www.gelbooru.com/index.php?page=post&s=random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def tbib(self, ctx: Context) -> None:
        """Random Image From TBIB"""
        try:
            query = "http://www.tbib.org/index.php?page=post&s=random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send("http:" + image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def xbooru(self, ctx: Context) -> None:
        """Random Image From Xbooru"""
        try:
            query = "http://xbooru.com/index.php?page=post&s=random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def furrybooru(self, ctx: Context) -> None:
        """Random Image From Furrybooru"""
        try:
            query = "http://furry.booru.org/index.php?page=post&s=random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def drunkenpumken(self, ctx: Context) -> None:
        """Random Image From DrunkenPumken"""
        try:
            query = "http://drunkenpumken.booru.org/index.php?page=post&s=random"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @is_nsfw()
    async def astolfo(self, ctx: Context) -> None:
        """Random Image From UnlimitedAstolfo"""
        try:
            query = "http://unlimitedastolfo.works/random_image/view"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="main_image").get("src")
            await ctx.send(f"http://unlimitedastolfo.works{image}")
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command()
    @guild_only()
    @is_nsfw()
    async def lolibooru(self, ctx: Context) -> None:
        """Random Image From Lolibooru"""
        try:
            query = "https://lolibooru.moe/post/random/"
            page = await (await self.bot.session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            image = image.replace(" ", "%20")
            await ctx.send(image)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @neko.command(aliases=["yan"])
    @is_nsfw()
    async def syandere(self, ctx: Context, tag: str = "yandere") -> None:
        """Searches Yande.re for NSFW pics."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://yande.re/post.json?limit=20&tags={tag}"
            ) as response:
                url = await response.json()

        await session.close()

        try:
            image = choice(url)
        except IndexError:
            await ctx.send("This tag doesn't exist... We couldn't find anything.")
            return

        image_url = image["sample_url"]

        embed = Embed(color=Color.blue())
        embed.title = f"Requested by {ctx.author.name}"
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)
