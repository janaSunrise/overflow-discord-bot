from bot import Bot
from .logging import LoggingSettings
from .roles import Roles


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(LoggingSettings(bot))
    bot.add_cog(Roles(bot))
