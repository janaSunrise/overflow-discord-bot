import random

import discord
from discord.ext.commands import (
    Cog,
    Context,
    command,
)

from bot import Bot


class Fun(Cog):
    """A cog designed for fun based commands."""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_agent = {"user-agent": "overflow discord bot"}
        self.all_facts = None

    @command()
    async def catfact(self, ctx: Context) -> None:
        """Get to know an interesting fact about cats."""
        async with self.bot.session.get("https://cat-fact.herokuapp.com/facts") as response:
            self.all_facts = await response.json()

        fact = random.choice(self.all_facts["all"])
        await ctx.send(
            embed=discord.Embed(
                title="Did you Know?",
                description=fact["text"],
                color=discord.Color.blurple()
            )
        )

    @command()
    async def chuck(self, ctx: Context) -> None:
        """Get a random Chuck Norris joke."""
        if random.randint(0, 1):
            async with self.bot.session.get("https://api.chucknorris.io/jokes/random") as r:
                joke = await r.json()
                await ctx.send(joke["value"])
                return

        async with self.bot.session.get("http://api.icndb.com/jokes/random") as response:
            joke = await response.json()
            await ctx.send(joke["value"]["joke"].replace("&quote", '"'))

    @command()
    async def cat(self, ctx: Context) -> None:
        """Get to see random cute cat images."""
        async with self.bot.session.get("https://some-random-api.ml/img/cat") as response:
            if response.status == 200:
                json = await response.json()
                embed = discord.Embed(
                    name="random.cat",
                    colour=discord.Color.blurple()
                )
                embed.set_image(url=json["link"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Couldn't Fetch cute cats. [CODE: {response.status}]")

    @command()
    async def dog(self, ctx: Context) -> None:
        """Get cute images of random dogs."""

        def decide_source() -> str:
            number = random.randint(0, 1)
            if number:
                return "https://random.dog/woof"
            return "https://dog.ceo/api/breeds/image/random"

        async with self.bot.session.get(decide_source(), headers=self.user_agent) as shibe_get:
            if shibe_get.status == 200:
                if shibe_get.host == "random.dog":
                    shibe_img = await shibe_get.text()
                    shibe_url = "https://random.dog/" + shibe_img

                elif shibe_get.host == "dog.ceo":
                    shibe_img = await shibe_get.json()
                    shibe_url = shibe_img["message"]

                if ".mp4" in shibe_url:
                    await ctx.send("video: " + shibe_url)
                else:
                    shibe_em = discord.Embed(colour=discord.Color.blurple())
                    shibe_em.set_image(url=shibe_url)
                    await ctx.send(embed=shibe_em)
            else:
                await ctx.send(f"Couldn't Fetch cute doggos :( [status : {shibe_get.status}]")

    @command()
    async def why(self, ctx: Context) -> None:
        """Getting to know a random `Why?` question"""
        async with self.bot.session.get("https://nekos.life/api/why", headers=self.user_agent) as resp:
            if resp.status == 200:
                json = await resp.json()
                embed = discord.Embed(
                    title=f"{ctx.author.name} wonders...",
                    description=json["why"],
                    colour=0x690E8
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Something went Boom! [CODE : {resp.status}]")

    @command(aliases=["shitjoke", "badjoke"])
    async def dadjoke(self, ctx: Context) -> None:
        """A simple shitty dad joke generator."""
        async with self.bot.session.get("https://icanhazdadjoke.com", headers=self.dadjoke) as joke:
            if joke.status == 200:
                res = await joke.text()
                res = res.encode("utf-8").decode("utf-8")
                await ctx.send(res)
            else:
                await ctx.send(f"No dad joke. [STATUS : {joke.status}]")

    @command(aliases=["techproblem"])
    async def excuse(self, ctx: Context) -> None:
        """Bastard Operator from Hell excuses."""
        async with self.bot.session.get("http://pages.cs.wisc.edu/~ballard/bofh/excuses") as resp:
            data = await resp.text()

        lines = data.split("\n")
        embed = discord.Embed(
            title="Excuses",
            description=random.choice(lines),
            color=discord.Color.blurple()
        )

        await ctx.send(embed=embed)

    @command()
    async def history(self, ctx: Context) -> None:
        """Get a random interesting history fact."""
        async with self.bot.session.get('http://numbersapi.com/random/date?json') as resp:
            res = await resp.json()
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="→ Random History Date!",
                description=f"• Fact: {res['text']}"
                            f"\n• Year: {res['year']}"
            )

            await ctx.send(embed=embed)

    @command()
    async def math(self, ctx: Context) -> None:
        """Get a random interesting math fact."""
        async with self.bot.session.get('http://numbersapi.com/random/math?json') as r:
            res = await r.json()
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="→ Random Math Fact!",
                description=f"• Fact: {res['text']}"
                            f"\n• Number: {res['number']}"
            )
            await ctx.send(embed=embed)

    @command()
    async def advice(self, ctx: Context) -> None:
        """Get a random advice."""
        async with self.bot.session.get('https://api.adviceslip.com/advice') as r:
            res = await r.json(content_type="text/html")
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="→ Random Advice!",
                description=f"• Advice: {res['slip']['advice']}"
            )

            await ctx.send(embed=embed)
