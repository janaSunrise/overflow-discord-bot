from bot import Bot

from .error import ErrorHandler
from .help import Help
from .sudo import Sudo


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(Help(bot))
    bot.add_cog(Sudo(bot))
