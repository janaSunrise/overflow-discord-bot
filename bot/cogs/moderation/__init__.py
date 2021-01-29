from bot import Bot

from .moderation import Moderation
from .lock import Lock


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Moderation(bot))
    bot.add_cog(Lock(bot))
