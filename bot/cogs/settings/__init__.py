from bot import Bot

from .roles import Roles


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Roles(bot))
