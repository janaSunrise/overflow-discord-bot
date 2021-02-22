import os

import discord

from bot import Bot, config


async def command_prefix(bot: Bot, message: discord.Message) -> str:
    """Define the prefix of the commands."""
    return await bot.get_prefix(message)


TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

intents = discord.Intents.all()
intents.presences = False

bot = Bot(
    command_prefix=command_prefix,
    intents=intents,
    activity=discord.Game(name=f"{PREFIX}help | Listening to coders!"),
    case_insensitive=True,
    owner_ids=config.devs
)

if __name__ == "__main__":
    bot.run(TOKEN)
