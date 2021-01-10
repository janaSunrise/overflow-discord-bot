import os

import discord

from bot import Bot

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "="
extensions = [
    "bot.cogs.hackernews",
    "bot.cogs.help",
    "bot.cogs.music",
    "bot.cogs.overflow",
    "bot.cogs.search",
    "bot.cogs.sudo"
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
