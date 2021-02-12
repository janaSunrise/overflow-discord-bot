from discord.ext import commands


class ModerationReason(commands.Converter):
    """Ensuring that the reason for moderation commands is within the specified limit of 512."""
    async def convert(self, ctx: commands.Context, argument: str) -> str:
        if not argument or argument == "":
            reason = f"Action carried out by {ctx.author} [{ctx.author.id}]"
        else:
            reason = f"{argument} by <@!{ctx.author.id}>"

            if len(reason) > 512:
                shorten_size = len(argument) - (512 - len(reason) + len(argument))
                raise commands.BadArgument(f"Your reason is too long! Please shorten it by {shorten_size}")

        return reason
