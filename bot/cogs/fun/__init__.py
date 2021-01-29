from bot import Bot

from .comics import Comics


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Comics(bot))
