import os

from discord import Game

from bot import Bot

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "="
extensions = [
    "cogs.overflow"
]

bot = Bot(
    extensions,
    command_prefix=PREFIX,
    activity=Game(name=f"{PREFIX}help | Listening to coders!"),
    case_insensitive=True,
)

if __name__ == "__main__":
    bot.run(TOKEN)
