from discord.ext import commands

from bot import Bot


class Moderation(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
