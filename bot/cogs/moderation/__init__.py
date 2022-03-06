from bot import Bot
from .lock import Lock
from .moderation import Moderation


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Moderation(bot))
    bot.add_cog(Lock(bot))
