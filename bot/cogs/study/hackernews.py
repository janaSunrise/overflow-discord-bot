import random
import typing as t
from textwrap import dedent

import discord
from discord.ext import tasks
from discord.ext.commands import Cog, Context, group

from bot import Bot
from bot.databases.hackernews_feed import HackernewsFeed
from bot.utils.pages import EmbedPages

NEWS_URL = "https://hacker-news.firebaseio.com/v0/"


class HackerNews(Cog):
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

                description = dedent(
                    f"""
                • Story ID: **{data["id"]}**
                • URL: [Here]({data.get("url")})
                • Score: **{data["score"]}**
                • Author: **{data["by"]}**
                """
                )

                embed = discord.Embed(
                    title=data["title"],
                    description=description,
                    color=discord.Color.blurple(),
                )
            article_embeds.append(embed)

        return article_embeds

    async def _generate_newsfeed_embed(self, article_numbers: list) -> discord.Embed:
        description = ""

        for item_id in article_numbers:
            async with self.bot.session.get(NEWS_URL + f"item/{item_id}.json") as resp:
                data = await resp.json()

                description += dedent(
                    f"""
                TITLE: **{data["title"]}**

                • Story ID: **{data["id"]}**
                • URL: [Here]({data.get("url")})
                • Score: **{data["score"]}**
                • Author: **{data["by"]}**\n
                """
                )

        embed = discord.Embed(
            title="Quick news feed!",
            description=description,
            color=discord.Color.blue(),
        )
        return embed

    @group(invoke_without_command=True)
    async def hackernews(self, ctx: Context) -> None:
        """Commands for hackernews and it's feeds."""
        await ctx.send_help(ctx.command)

    @hackernews.command(name="new-stories")
    async def new_stories(self, ctx: Context, count: int = 5) -> None:
        """Get all the newest and fresh hacker news."""
        if not 1 < count < 20:
            await ctx.send(":x: You cannot view more than 20 Stories or less than 2!")

        async with self.bot.session.get(NEWS_URL + "newstories.json") as resp:
            data = await resp.json()

        article_numbers = random.sample(data, count)
        article_embeds = await self._generate_embeds(article_numbers)

        await EmbedPages(article_embeds).start(ctx)

    @hackernews.command(name="top-stories")
    async def top_stories(self, ctx: Context, count: int = 5) -> None:
        """Get all the trending hacker news."""
        if not 1 < count < 20:
            await ctx.send(":x: You cannot view more than 20 Stories or less than 2!")

        async with self.bot.session.get(NEWS_URL + "topstories.json") as resp:
            data = await resp.json()

        article_numbers = random.sample(data, count)
        article_embeds = await self._generate_embeds(article_numbers)

        await EmbedPages(article_embeds).start(ctx)

    @hackernews.command(manage_channels=True)
    async def subscribe(
        self, ctx: Context, channel: t.Optional[discord.TextChannel] = None
    ) -> None:
        """Subscribe to the scheduled hacker news feed."""
        if not channel:
            await ctx.send("Please specify a channel to send the feed!")
            return

        await HackernewsFeed.set_feed_channel(
            self.bot.database, ctx.guild.id, channel.id
        )
        await ctx.send(f"Congrats :tada: Set {channel.mention} as the feed channel!")

    @hackernews.command(manage_channels=True)
    async def unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe from the scheduled hacker news feed."""
        row = await HackernewsFeed.get_feed_channel(self.bot.database, ctx.guild.id)

        if not row:
            await ctx.send(":x: You're already unsubscribed from the feed!")
        else:
            await HackernewsFeed.remove_feed_channel(self.bot.database, ctx.guild.id)
            await ctx.send("Aww :( We hate to see you unsubscribe from the feed!")

    @tasks.loop(hours=24)
    async def send_feed(self) -> None:
        async with self.bot.session.get(NEWS_URL + "topstories.json") as resp:
            data = await resp.json()

        article_numbers = random.sample(data, 6)
        article_embed = await self._generate_newsfeed_embed(article_numbers)

        rows = await HackernewsFeed.get_feed_channels(self.bot.database)
        if rows is not None:
            channels = [row["channel_id"] for row in rows]

            for channel in channels:
                channel = self.bot.get_channel(channel)
                await channel.send("Here's your feed :tada:", embed=article_embed)
