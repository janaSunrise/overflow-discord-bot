from discord.ext.commands import CommandError


class NoChannelProvided(CommandError):
    """Error raised when no suitable voice channel was supplied."""


class IncorrectChannelError(CommandError):
    """Error raised when commands are issued outside of the players session channel."""


class InvalidRepeatMode(CommandError):
    pass
