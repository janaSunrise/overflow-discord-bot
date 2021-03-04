from bot import Bot

from .announcements import Announcements
from .embeds import Embeds
from .lookup import Lookup


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Announcements(bot))
    bot.add_cog(Embeds(bot))
    bot.add_cog(Lookup(bot))
