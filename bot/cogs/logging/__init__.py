from bot import Bot

from .voice_log import VoiceLog


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(VoiceLog(bot))
