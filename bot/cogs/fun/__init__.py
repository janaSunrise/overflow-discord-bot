from bot import Bot

from .comics import Comics
from .fun import Fun
from .reddit import Reddit


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Comics(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Reddit(bot))
