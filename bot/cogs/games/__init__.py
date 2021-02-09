from bot import Bot

from .games import Games


def setup(bot: Bot) -> None:
    bot.add_cog(Games(bot))
