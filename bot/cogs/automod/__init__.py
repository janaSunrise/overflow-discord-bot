from bot import Bot

from .file_security import FileSecurity


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(FileSecurity(bot))
