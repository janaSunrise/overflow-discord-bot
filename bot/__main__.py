import os

import discord

from bot import Bot, config

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX
extensions = [
    # Cog packages
    "bot.cogs.core",
    "bot.cogs.coding",
    "bot.cogs.fun",
    "bot.cogs.games",
    "bot.cogs.moderation",
    "bot.cogs.utility",
    "bot.cogs.study",
    
    # Cogs
    "bot.cogs.commands",
    "bot.cogs.info",
    "bot.cogs.music",
]

intents = discord.Intents.all()
intents.presences = False

bot = Bot(
    extensions=extensions,
    command_prefix=PREFIX,
    intents=intents,
    activity=discord.Game(name=f"{PREFIX}help | Listening to coders!"),
    case_insensitive=True,
    owner_ids=config.devs
)

if __name__ == "__main__":
    bot.run(TOKEN)
