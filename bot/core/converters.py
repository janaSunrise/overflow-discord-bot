import re

from dateutil.relativedelta import relativedelta
from discord.ext.commands import BadArgument, Context, Converter

TIME_REGEX = re.compile(
    r"((?P<years>\d+?) ?(y|yr|yrs|year|years) ?)?"
    r"((?P<months>\d+?) ?(mon|months|month) ?)?"
    r"((?P<weeks>\d+?) ?(w|wk|weeks|week) ?)?"
    r"((?P<days>\d+?) ?(d|days|day) ?)?"
    r"((?P<hours>\d+?) ?(h|hr|hrs|hours|hour) ?)?"
    r"((?P<minutes>\d+?) ?(m|min|mins|minutes|minute) ?)?"
    r"((?P<seconds>\d+?) ?(s|sec|secs|seconds|second))?",
    re.IGNORECASE,
)


class ModerationReason(Converter):
    """Ensuring that the reason for moderation commands is within the specified limit of 512."""

    async def convert(self, ctx: Context, argument: str) -> str:
        if not argument or argument == "":
            reason = f"Action carried out by {ctx.author} [{ctx.author.id}]"
        else:
            reason = f"{argument} by <@!{ctx.author.id}>"

            if len(reason) > 512:
                shorten_size = len(argument) - \
                    (512 - len(reason) + len(argument))
                raise BadArgument(
                    f"Your reason is too long! Please shorten it by {shorten_size}"
                )

        return reason


class TimeConverter(Converter):
    async def convert(self, ctx: Context, duration: str) -> relativedelta:
        time_group = TIME_REGEX.fullmatch(duration)

        if not time_group:
            raise BadArgument("Invalid duration has been specified.")
        duration_dict = {
            unit: int(amount)
            for unit, amount in time_group.groupdict(default=0).items()
        }

        return relativedelta(**duration_dict)
