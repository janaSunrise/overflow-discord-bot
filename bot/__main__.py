import os

import discord
from discord.ext.commands import when_mentioned_or

from bot import Bot, config


async def command_prefix(bot: Bot, message: discord.Message) -> str:
    """Define the prefix of the commands."""
    return when_mentioned_or(await bot.get_msg_prefix(message))(bot, message)


TOKEN = os.getenv("BOT_TOKEN")
PREFIX = config.COMMAND_PREFIX

intents = discord.Intents.all()
intents.presences = False

bot = Bot(
    command_prefix=command_prefix,
    intents=intents,
    activity=discord.Game(name=f"{PREFIX}help | Busy coding with developers!"),
    case_insensitive=True,
    owner_ids=config.devs,
    heartbeat_timeout=150.0,
)

if __name__ == "__main__":
    bot.run(TOKEN)
