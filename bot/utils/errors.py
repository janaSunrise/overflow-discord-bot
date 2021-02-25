from discord.ext.commands import CommandError


class NoChannelProvided(CommandError):
    """Error raised when no suitable voice channel was supplied."""

    pass


class IncorrectChannelError(CommandError):
    """Error raised when commands are issued outside of the players session channel."""

    pass


class InvalidRepeatMode(CommandError):
    pass
