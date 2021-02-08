import random

import discord
from discord.ext import commands

from bot import Bot


class Fun(commands.Cog):
    """A cog designed for fun based commands."""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_agent = {"user-agent": "overflow discord bot"}
        self.all_facts = None

    @commands.command()
    async def catfact(self, ctx: commands.Context) -> None:
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

    @commands.command()
    async def chuck(self, ctx: commands.Context) -> None:
        """Get a random Chuck Norris joke."""
        if random.randint(0, 1):
            async with self.bot.session.get("https://api.chucknorris.io/jokes/random") as r:
                joke = await r.json()
                await ctx.send(joke["value"])
                return

        async with self.bot.session.get("http://api.icndb.com/jokes/random") as response:
            joke = await response.json()
            await ctx.send(joke["value"]["joke"].replace("&quote", '"'))

    @commands.command()
    async def cat(self, ctx: commands.Context) -> None:
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

    @commands.command()
    async def dog(self, ctx: commands.Context) -> None:
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


