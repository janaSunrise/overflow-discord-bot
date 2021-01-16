import random
from textwrap import dedent
import typing as t

import discord
from discord.ext import commands, tasks

from bot import Bot
from bot.utils.pages import EmbedPages

NEWS_URL = "https://hacker-news.firebaseio.com/v0/"


class HackerNews(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.send_feed.start()

    def cog_unload(self):
        self.send_feed.cancel()

    async def _generate_embeds(self, article_numbers: list) -> t.List[discord.Embed]:
        article_embeds = []

        for item_id in article_numbers:
            async with self.bot.session.get(NEWS_URL + f"item/{item_id}.json") as resp:
                data = await resp.json()

                description = dedent(f"""
                • Story ID: **{data["id"]}**
                • URL: [Here]({data.get("url")})
                • Score: **{data["score"]}**
                • Author: **{data["by"]}**
                """)

                embed = discord.Embed(
                    title=data["title"],
                    description=description,
                    color=discord.Color.blurple()
                )
            article_embeds.append(embed)

        return article_embeds

    async def _generate_newsfeed_embed(self, article_numbers: list) -> list:
        description = ""

        for item_id in article_numbers:
            async with self.bot.session.get(NEWS_URL + f"item/{item_id}.json") as resp:
                data = await resp.json()

                description += dedent(f"""
                TITLE: **{data["title"]}**

                • Story ID: **{data["id"]}**
                • URL: [Here]({data.get("url")})
                • Score: **{data["score"]}**
                • Author: **{data["by"]}**\n
                """)

        embed = discord.Embed(
            title="Quick news feed!",
            description=description,
            color=discord.Color.blue()
        )
        return embed

    @commands.command(name="new-stories")
    async def new_stories(self, ctx: commands.Context, count: int = 5) -> None:
        """
        Get all the newest and fresh hacker news.
        """
        if not 1 < count < 20:
            await ctx.send(":x: You cannot view more than 20 Stories or less than 2!")

        async with self.bot.session.get(NEWS_URL + "newstories.json") as resp:
            data = await resp.json()

        article_numbers = random.sample(data, count)
        article_embeds = await self._generate_embeds(article_numbers)

        await EmbedPages(article_embeds).start(ctx)

    @commands.command(name="top-stories")
    async def top_stories(self, ctx: commands.Context, count: int = 5) -> None:
        """
        Get all the trending hacker news.
        """
        if not 1 < count < 20:
            await ctx.send(":x: You cannot view more than 20 Stories or less than 2!")

        async with self.bot.session.get(NEWS_URL + "topstories.json") as resp:
            data = await resp.json()

        article_numbers = random.sample(data, count)
        article_embeds = await self._generate_embeds(article_numbers)

        await EmbedPages(article_embeds).start(ctx)

    @commands.command()
    async def subscribe(self, ctx: commands.Context, channel: t.Optional[discord.TextChannel] = None) -> None:
        """
        Subscribe to the scheduled hacker news feed.
        """
        if not channel:
            await ctx.send("Please specify a channel to send the feed!")
            return

        async with self.bot.db.execute("SELECT * FROM newsfeed WHERE guild_id=?", (ctx.guild.id,)) as cursor:
            row = await cursor.fetchone()

        if not row:
            await self.bot.db.execute("INSERT INTO newsfeed VALUES (?, ?)", (ctx.guild.id, channel.id))
            await self.bot.db.commit()

            await ctx.send("Congrats :tada: You're now subscribed to the feed!")
        else:
            await ctx.send(":x: You're already subscribed to the feed!")

    @commands.command()
    async def unsubscribe(self, ctx: commands.Context) -> None:
        """
        Unsubscribe from the scheduled hacker news feed.
        """
        async with self.bot.db.execute("SELECT * FROM newsfeed WHERE guild_id=?", (ctx.guild.id,)) as cursor:
            row = await cursor.fetchone()

        if not row:
            await ctx.send(":x: You're already unsubscribed from the feed!")
        else:
            await self.bot.db.execute("DELETE FROM newsfeed where guild_id=?", (ctx.guild.id,))
            await self.bot.db.commit()

            await ctx.send("Aww :( We hate to see you unsubscribe from the feed!")

    @tasks.loop(hours=24)
    async def send_feed(self) -> None:
        async with self.bot.session.get(NEWS_URL + "topstories.json") as resp:
            data = await resp.json()

        article_numbers = random.sample(data, 6)
        article_embed = await self._generate_newsfeed_embed(article_numbers)

        async with self.bot.db.execute("SELECT * FROM newsfeed") as cursor:
            channels = [row[1] for row in (await cursor.fetchall())]

            for channel in channels:
                channel = self.bot.get_channel(channel)
                await channel.send("Here's your feed :tada:", embed=article_embed)


def setup(bot: Bot) -> None:
    bot.add_cog(HackerNews(bot))
