import os
import random

from asyncpraw import Reddit as RedditAPI
from asyncpraw.exceptions import MissingRequiredAttributeException
from discord.ext.commands import Cog, Context, group, is_nsfw
from loguru import logger

from bot import Bot
from bot.config import nsfw_subreddits_list as nsfw_subreddits
from bot.config import subreddits_list as subreddits
from bot.utils.embeds import reddit_embed


class Nsfw(Cog):
    """NSFW, Pictures of the nature."""
    def __init__(self, bot: Bot) -> None:
        try:
            self.reddit_client = RedditAPI(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=os.getenv("REDDIT_USER_AGENT"),
                username=os.getenv("REDDIT_USERNAME"),
            )
        except MissingRequiredAttributeException:
            logger.error(
                "Reddit cog requires correct enviroment variables to run.")
            self.cog_unload()
        self.bot = bot

    @group(invoke_without_command=True)
    async def nsfw(self, ctx: Context) -> None:
        """Nsfw commands."""
        await ctx.send_help(ctx.command)

    @nsfw.command()
    @is_nsfw()
    async def img(self, ctx: Context) -> None:
        """Get a NSFW picture."""
        name = random.choice(subreddits["nsfw"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    async def new(self, ctx: Context, subreddit: str) -> None:
        """Retrieve fresh posts from the given subreddit."""
        subreddit = await self.reddit_client.subreddit(subreddit, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
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

    @nsfw.command()
    async def hot(self, ctx: Context, subreddit: str) -> None:
        """Retrieve the hottest posts from the given subreddit."""
        subreddit = await self.reddit_client.subreddit(subreddit, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
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

    @nsfw.command(name="4k")
    @is_nsfw()
    async def _4k(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        name = random.choice(nsfw_subreddits["fourk"])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def ass(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "ass"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def anal(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "anal"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def bdsm(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "bdsm"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def blowjob(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "blowjob"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if (
            "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url
        ):
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def cunnilingus(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "cunnilingus"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def bottomless(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "bottomless"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def cumshots(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "cumshots"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def deepthroat(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "deepthroat"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def dick(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "dick"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def doublepenetration(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "double_penetration"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def gay(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "gay"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def hentai(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "hentai"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def lesbian(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "lesbian"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def public(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "public"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def rule34(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "rule34"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def trap(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "trap"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def boobs(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "boobs"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def ahegao(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "ahegao"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def group(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "group"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def milf(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "milf"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def thigh(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "thigh"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def redhead(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "redhead"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)

    @nsfw.command()
    @is_nsfw()
    async def wild(self, ctx: Context) -> None:
        """Shows a NSFW Picture."""
        sub = "wild"
        name = random.choice(nsfw_subreddits[sub])
        subreddit = await self.reddit_client.subreddit(name, fetch=True)
        randompost = random.choice(
            [post async for post in subreddit.hot() if not post.is_self]
        )

        embed = await reddit_embed(subreddit, randompost)
        await ctx.send(embed=embed)
        if "https://v.redd.it/" in randompost.url or "https://youtube.com/" in randompost.url:
            await ctx.send(randompost.url)
