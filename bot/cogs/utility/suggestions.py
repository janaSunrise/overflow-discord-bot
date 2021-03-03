import discord
from discord.ext.commands import Cog

from bot import Bot


class Suggestions(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
