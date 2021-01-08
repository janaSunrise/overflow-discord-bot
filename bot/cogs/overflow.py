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
    def get_response_string(query) -> str:
        query_data = query.json
        check = ' :white_check_mark:' if query.json['is_answered'] else ''
        return f"|{query_data['score']}|{check} <{query.url}|{query.title}> ({query_data['answer_count']} answers)"

    @commands.command(aliases=["overflow", "stack", "stacksearch"])
    def stackoverflow(self, ctx, *, query: str) -> None:
        try:
            qs = self.so.search(intitle=query, sort=Sort.Votes, order=DESC)
        except UnicodeEncodeError:
            await ctx.send(f"Only English language is supported. '{query}' is not valid input.")

        resp_qs = [f'Stack Overflow Top Questions for "{query}"\n']
        resp_qs.extend(map(
            self.get_response_string, qs[:self.MAX_QUESTIONS]
        ))

        if len(resp_qs) is 1:
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