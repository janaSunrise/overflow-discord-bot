import os
from html import unescape
from urllib.parse import quote_plus

import discord
from discord.ext.commands import BucketType, Cog, Context, command, cooldown

from bot import Bot

SE_KEY = os.getenv("SE_KEY")

BASE_URL = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow&q={query}"
SEARCH_URL = "https://stackoverflow.com/search?q={query}"


class Overflow(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.MAX_QUESTIONS = 6

    @command(aliases=["overflow", "stack", "stacksearch"])
    @cooldown(1, 15, BucketType.user)
    async def stackoverflow(self, ctx: Context, *, query: str) -> None:
        """Search stackoverflow for a query."""
        async with self.bot.session.get(
            BASE_URL.format(query=quote_plus(query))
        ) as response:
            data = await response.json()

        top = data["items"][: self.MAX_QUESTIONS]
        embed = discord.Embed(
            title=f"Stack Overflow Top Questions for {query!r}",
            url=SEARCH_URL.format(query=quote_plus(query)),
            description=f"Here are the top {len(top)} results:",
            color=discord.Color.blurple(),
        )

        for item in top:
            embed.add_field(
                name=f"{unescape(item['title'])}",
                value=(
                    f"{item['score']} upvote{'s' if item['score'] != 1 else ''} ┃ "
                    f"{item['answer_count']} answer{'s' if item['answer_count'] != 1 else ''} ┃ "
                    f"Tags: {', '.join(item['tags'])} ┃ "
                    f"[LINK here]({item['link']})"
                ),
                inline=False,
            )

        await ctx.send(embed=embed)
