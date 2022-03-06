from bot import Bot
from .announcements import Announcements
from .embeds import Embeds
from .lookup import Lookup
# from .suggestions import Suggestions


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Announcements(bot))
    bot.add_cog(Embeds(bot))
    bot.add_cog(Lookup(bot))
    # bot.add_cog(Suggestions(bot))
