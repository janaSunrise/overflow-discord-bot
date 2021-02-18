from bot import Bot

from .conversion import Conversion
from .hackernews import HackerNews
from .nasa import Nasa
from .study import Study


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Conversion(bot))
    bot.add_cog(HackerNews(bot))
    bot.add_cog(Nasa(bot))
    bot.add_cog(Study(bot))
