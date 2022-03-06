import typing as t
from datetime import datetime
from textwrap import dedent

import discord
from asyncpraw import Reddit as RedditAPI
from discord.ext.commands import Context, MemberConverter, UserConverter

from bot.core.converters import ModerationReason


def moderation_embed(
    ctx: Context,
    action: str,
    user: t.Union[discord.Member, MemberConverter, discord.User, UserConverter],
    reason: t.Union[str, ModerationReason],
    color: discord.Color = discord.Color.blue(),  # noqa: B008
) -> discord.Embed:
    """Return a quick embed for moderation event."""
    description = dedent(f"""
    User: {user.mention} [`{user.id}`]
    Reason: {reason}

    Moderator: {ctx.author} [`{ctx.author.id}`]
    """)

    embed = discord.Embed(
        title=f"User {action}ed",
        description=description,
        color=color,
        timestamp=datetime.utcnow(),
    )
    return embed


async def reddit_embed(subreddit: str, randompost: RedditAPI.submission) -> discord.Embed:
    """Make a reddit post an embed."""
    embed = discord.Embed(colour=discord.Color.green(), url=randompost.url)

    if 0 < len(randompost.title) < 256:
        embed.title = randompost.title
    elif len(randompost.title) > 256:
        embed.title = f"{randompost.title[:200]}..."

    if 0 < len(randompost.selftext) < 2048:
        embed.description = randompost.selftext
    elif len(randompost.selftext) > 2048:
        embed.description = f"{randompost.selftext[:2000]} | Read more..."

    if not randompost.url.startswith("https://v.redd.it/") or randompost.url.startswith(
        "https://youtube.com/"
    ):
        imgur_links = (
            "https://imgur.com/",
            "https://i.imgur.com/",
            "http://i.imgur.com/",
            "http://imgur.com",
            "https://m.imgur.com",
        )
        accepted_extensions = (".png", ".jpg", ".jpeg", ".gif")

        url = randompost.url

        if url.startswith(imgur_links):
            if url.endswith(".mp4"):
                url = url[:-3] + "gif"

            elif url.endswith(".gifv"):
                url = url[:-1]

            elif url.endswith(accepted_extensions):
                url = url

            else:
                url = url + ".png"

        elif url.startswith("https://gfycat.com/"):
            url_cut = url.replace("https://gfycat.com/", "")

            url = f"https://thumbs.gfycat.com/{url_cut}-size_restricted.gif"

        elif url.endswith(accepted_extensions):
            url = url

        embed.set_image(url=url)

    comments = await randompost.comments()
    embed.set_footer(text=f"👍 {randompost.score} | 💬 {len(comments)}")

    await randompost.author.load()
    embed.set_author(
        name=f"u/{randompost.author.name}",
        icon_url=randompost.author.icon_img,
        url=f"https://www.reddit.com/user/{randompost.author.name}",
    )

    embed.add_field(
        name="SubReddit",
        value=f"[r/{subreddit}](https://www.reddit.com/r/{subreddit}/)",
        inline=False,
    )

    return embed
