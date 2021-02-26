import random

import discord
from discord.ext import tasks
from discord.ext.commands import Cog, Context, command

from bot import Bot, config

from .blackjack import Blackjack, Blackjack_players
from .connect4 import Connect4
from .hangman import HangmanGame
from .tic_tac_toe import TTT_Game


class Games(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.blackjack_list = []
        self.blackjack_updater.start()

        self._in_game = {}
        self._hit = {}

    def cog_unload(self) -> None:
        self.blackjack_updater.cancel()

    @tasks.loop(seconds=5)
    async def blackjack_updater(self) -> None:
        new = []
        for black in self.blackjack_list:
            if black.current_state == 1:
                await black.updater()
            elif black.current_state == -1:
                continue
            new.append(black)
        self.blackjack_list = new

    @command(ignore_extra=True)
    async def blackjack(self, ctx: Context, cost: int = 5) -> None:
        """
        Rules: if it's your turn, press the button corresponding to the column in which you want to place the card.
        If you want to split (play on one more column, up to a max of 3, press :regional_indicator_3: ). If you want to
        stop, press :x:.
        To win, you must score more than the dealer, but no more than 21 (each card's value is its pip value,
        except for faces, which are worth 10 points, and the Ace, which is worth either 1 or 11).
        An Ace plus a face is called a blackjack and beats a 21
        """
        if cost < 0:
            await ctx.send("You can't bet negative money")

        players, money_dict = await Blackjack_players(ctx.author, 100, cost, delete_message_after=True).prompt(ctx)

        if not players:
            await ctx.send("Nobody wants to play")
            return

        await Blackjack(players, money_dict, cost, clear_reactions_after=True).prompt(ctx)

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

        embed = discord.Embed(title="Magic 8-ball",
                              color=discord.Color.blurple())
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
        winner = await Connect4(ctx.author, member, clear_reactions_after=True).prompt(
            ctx
        )
        if winner:
            await ctx.send(f"{winner.mention} won !")
        else:
            await ctx.send("Game cancelled")
