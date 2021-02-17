from bot import Bot

from .embeds import Embeds


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(Embeds(bot))
