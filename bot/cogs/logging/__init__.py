from bot import Bot

from .join_log import JoinLog
from .member_log import MemberLog
from .voice_log import VoiceLog


def setup(bot: Bot) -> None:
    """Load the cogs."""
    bot.add_cog(JoinLog(bot))
    bot.add_cog(MemberLog(bot))
    bot.add_cog(VoiceLog(bot))
