from bot import Bot

from .file_security import FileSecurity
from .mod_lock import ModerationLock
from .swear_filter import SwearFilter


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(FileSecurity(bot))
    bot.add_cog(ModerationLock(bot))
    bot.add_cog(SwearFilter(bot))
