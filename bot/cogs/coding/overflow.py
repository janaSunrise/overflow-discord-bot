import os

import discord
from discord.ext import commands
from stackexchange import Site, StackOverflow, Sort, DESC

from bot import Bot

SE_KEY = os.getenv("SE_KEY")


class Overflow(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.MAX_QUESTIONS = 6
        self.so = Site(StackOverflow, SE_KEY)

    @staticmethod
    async def get_response_string(query) -> str:
        query_data = query.json
        check = ' :white_check_mark:' if query.json['is_answered'] else ''
        return f"|{query_data['score']}|{check} [{query.title}]({query.url}) ({query_data['answer_count']} answers)"\
            .replace("&amp;", "&").replace("&lt;", ">").replace("&gt;", ">")

    @commands.command(aliases=["overflow", "stack", "stacksearch"])
    async def stackoverflow(self, ctx, *, query: str) -> None:
        """
        Search stackoverflow for a query.
        """
        try:
            qs = self.so.search(intitle=query, sort=Sort.Votes, order=DESC)
        except UnicodeEncodeError:
            await ctx.send(f"Only English language is supported. '{query}' is not valid input.")

        resp_qs = [f'Stack Overflow Top Questions for "{query}"\n']

        for question in qs[:self.MAX_QUESTIONS]:
            resp_qs.append(
                await self.get_response_string(question)
            )

        if len(resp_qs) == 1:
            resp_qs.append((
                'No questions found. Please try a broader search or search directly on '
                '[Stack Overflow](https://stackoverflow.com)'
            ))

        description = '\n'.join(resp_qs)

        embed = discord.Embed(
            title="Stack overflow search",
            description=description,
            colour=discord.Color.blurple()
        )

        await ctx.send(embed=embed)
