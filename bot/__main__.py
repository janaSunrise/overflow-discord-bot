import os

import discord

from bot import Bot, config

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX
extensions = [
    # Cog packages
    "bot.cogs.coding",
    "bot.cogs.fun",
    "bot.cogs.moderation",
    "bot.cogs.study",
    
    # Cogs
    "bot.cogs.commands",
    "bot.cogs.conversion",
    "bot.cogs.help",
    "bot.cogs.info",
    "bot.cogs.music",
    "bot.cogs.sudo",
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
