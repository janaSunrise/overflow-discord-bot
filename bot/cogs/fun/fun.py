from discord.ext import commands

from bot import Bot


class Fun(commands.Cog):
    """A cog designed for fun based commands."""
    def __init__(self, bot: Bot):
        self.bot = bot
