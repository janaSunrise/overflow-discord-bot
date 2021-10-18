import os
import random

from asyncpraw import Reddit as RedditAPI
from asyncpraw.exceptions import MissingRequiredAttributeException
from discord.ext.commands import Cog, Context, group, is_nsfw
from loguru import logger

from bot import Bot
from bot.config import subreddits_list as subreddits
from bot.utils.embeds import reddit_embed


class Reddit(Cog):
    """Reddit, the front page of the Internet."""

    def __init__(self, bot: Bot) -> None:
        try:
            self.reddit_client = RedditAPI(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
                username=os.getenv("REDDIT_USERNAME"),
            )
        except MissingRequiredAttributeException:
            logger.error("Reddit cog requires correct environment variables to run.")
            self.cog_unload()
        self.bot = bot

    @group(invoke_without_command=True)
    async def reddit(self, ctx: Context) -> None:
        """Reddit commands."""
        await ctx.send_help(ctx.command)

    @reddit.command(aliases=["meme"])
    async def memes(self, ctx: Context) -> None:
        """Get random memes."""
        name = random.choice(subreddits["memes"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url
            or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @reddit.command()
    async def funny(self, ctx: Context) -> None:
        """Get a funny picture."""
        name = random.choice(subreddits["funny"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url
            or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @reddit.command()
    @is_nsfw()
    async def nsfw(self, ctx: Context) -> None:
        """Get a NSFW picture."""
        name = random.choice(subreddits["nsfw"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url
            or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @reddit.command()
    async def aww(self, ctx: Context) -> None:
        """Get a random aww picture."""
        name = random.choice(subreddits["aww"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )
        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url
            or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @reddit.command()
    async def science(self, ctx: Context) -> None:
        """Get a science fact."""
        name = random.choice(subreddits["sci"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url
            or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @reddit.command()
    async def new(self, ctx: Context, subreddit: str) -> None:
        """Retrieve fresh posts from the given subreddit."""
        sub = await self.reddit_client.subreddit(subreddit, fetch=True)
        randompost = random.choice(
            [post async for post in sub.new() if not post.is_self]
        )

        if randompost.over_18:
            if ctx.channel.is_nsfw():
                if "https://v.redd.it/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)
                elif "https://youtube.com/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)
                else:
                    embed = await reddit_embed(subreddit, randompost)
                    await ctx.send(embed=embed)

            else:
                await ctx.send(
                    "**STOP!** , **NSFW** commands can only be used in NSFW channels"
                )
        else:
            if "https://v.redd.it/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            elif "https://youtube.com/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            else:
                embed = await reddit_embed(subreddit, randompost)
                await ctx.send(embed=embed)

    @reddit.command()
    async def hot(self, ctx: Context, subreddit: str) -> None:
        """Retrieve the hottest posts from the given subreddit."""
        sub = await self.reddit_client.subreddit(subreddit, fetch=True)
        randompost = random.choice(
            [post async for post in sub.hot() if not post.is_self]
        )

        if randompost.over_18:
            if ctx.channel.is_nsfw():
                if "https://v.redd.it/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)
                elif "https://youtube.com/" in randompost.url:
                    await ctx.send(randompost.title)
                    await ctx.send(randompost.url)

                else:
                    embed = await reddit_embed(subreddit, randompost)
                    await ctx.send(embed=embed)
            else:
                await ctx.send(
                    "**STOP!** , **NSFW** commands can only be used in NSFW channels"
                )
        else:
            if "https://v.redd.it/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)
            elif "https://youtube.com/" in randompost.url:
                await ctx.send(randompost.title)
                await ctx.send(randompost.url)

            else:
                embed = await reddit_embed(subreddit, randompost)
                await ctx.send(embed=embed)
