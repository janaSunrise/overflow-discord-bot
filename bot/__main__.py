import os

import discord

from bot import Bot

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "="
extensions = [
    "bot.cogs.overflow"
]

intents = discord.Intents.all()
intents.presences = False
intents.members = False

bot = Bot(
    extensions,
    command_prefix=PREFIX,
    intents=intents,
    activity=discord.Game(name=f"{PREFIX}help | Listening to coders!"),
    case_insensitive=True,
)

if __name__ == "__main__":
    bot.run(TOKEN)
