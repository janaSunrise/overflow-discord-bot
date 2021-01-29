from bot import Bot

from .moderation import Moderation


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Moderation(bot))
