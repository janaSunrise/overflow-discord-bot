import discord
from discord.ext import commands

from bot import Bot
from .tic_tac_toe import TTT_Game


class Games(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(aliases=["ttt", "tictactoe"])
    async def tic_tac_toe(self, ctx: commands.Context, opponent: discord.Member = None) -> None:
        """Play a game of Tic-Tac-Toe."""
        game = TTT_Game(ctx.author, opponent, clear_reactions_after=True)
        await game.start(ctx)
