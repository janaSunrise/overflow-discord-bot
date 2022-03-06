from bot import Bot
from .eval import Eval
from .github import Github
from .overflow import Overflow
from .search import Search


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Eval(bot))
    bot.add_cog(Github(bot))
    bot.add_cog(Overflow(bot))
    bot.add_cog(Search(bot))
