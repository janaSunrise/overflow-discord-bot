import random

import discord
from discord.ext import commands

from bot import Bot


class Fun(commands.Cog):
    """A cog designed for fun based commands."""
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def catfact(self, ctx: commands.Context) -> None:
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
