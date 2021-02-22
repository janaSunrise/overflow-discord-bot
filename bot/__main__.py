import os

import discord

from bot import Bot, config

TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

intents = discord.Intents.all()
intents.presences = False

bot = Bot(
    command_prefix=PREFIX,
    intents=intents,
    activity=discord.Game(name=f"{PREFIX}help | Listening to coders!"),
    case_insensitive=True,
    owner_ids=config.devs
)

if __name__ == "__main__":
    bot.run(TOKEN)
