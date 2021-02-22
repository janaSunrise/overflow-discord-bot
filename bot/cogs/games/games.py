import random

import discord
from discord.ext.commands import (
    Cog,
    Context,
    command
)

from bot import Bot, config
from .connect4 import Connect4
from .hangman import HangmanGame
from .tic_tac_toe import TTT_Game


class Games(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(aliases=["8ball"])
    async def ball8(self, ctx: Context, *, question: str) -> None:
        """Ask the all-knowing 8ball your questions and get your answers."""
        reply_type = random.randint(1, 3)

        if reply_type == 1:
            answer = random.choice(config.BALL_REPLIES["positive"])
        elif reply_type == 2:
            answer = random.choice(config.BALL_REPLIES["negative"])
        elif reply_type == 3:
            answer = random.choice(config.BALL_REPLIES["error"])

        embed = discord.Embed(title="Magic 8-ball", color=discord.Color.blurple())
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Answer", value=answer)

        await ctx.send(embed=embed)

    @command(aliases=["ttt", "tictactoe"])
    async def tic_tac_toe(self, ctx: Context, opponent: discord.Member = None) -> None:
        """Play a game of Tic-Tac-Toe."""
        game = TTT_Game(ctx.author, opponent, clear_reactions_after=True)
        await game.start(ctx)

    @command()
    async def hangman(self, ctx: Context) -> None:
        """Play game of Hangman."""
        hangman_game = HangmanGame.random(ctx)
        await hangman_game.play()

    @command(aliases=["c4"])
    async def connect4(self, ctx: Context, member: discord.Member) -> None:
        """Play connect 4 with a friend"""
        winner = await Connect4(ctx.author, member, clear_reactions_after=True).prompt(ctx)
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")
