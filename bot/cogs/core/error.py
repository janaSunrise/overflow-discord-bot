import textwrap
import typing as t

from discord import Color, Embed
from discord.ext.commands import (
    BucketType,
    BotMissingPermissions,
    BotMissingRole,
    Cog,
    Context,
    CommandOnCooldown,
    DisabledCommand,
    ExpectedClosingQuoteError,
    InvalidEndOfQuotedStringError,
    MaxConcurrencyReached,
    MissingPermissions,
    MissingRole,
    NotOwner,
    NoPrivateMessage,
    NSFWChannelRequired,
    PrivateMessageOnly,
    UnexpectedQuoteError,
    errors
)
from loguru import logger

from bot import Bot
from bot.utils.errors import IncorrectChannelError, InvalidRepeatMode, NoChannelProvided
from bot.utils.utils import format_time


class ErrorHandler(Cog):
    """This cog handles the errors invoked from commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def error_embed(
            self, ctx: Context, title: t.Optional[str] = None, description: t.Optional[str] = None
    ) -> None:
        await ctx.send(
            embed=Embed(
                title=title,
                description=description,
                color=Color.red()
            )
        )

    async def command_syntax_error(self, ctx: Context, error: errors.UserInputError) -> None:
        command = ctx.command
        parent = command.full_parent_name

        command_name = str(command) if not parent else f"{parent} {command.name}"
        command_syntax = f"```{command_name} {command.signature}```"

        aliases = [f"`{alias}`" if not parent else f"`{parent} {alias}`" for alias in command.aliases]
        aliases = ", ".join(sorted(aliases))

        command_help = f"{command.help or 'No description provided.'}"

        await self.error_embed(
            ctx,
            title="Invalid command syntax",
            description=textwrap.dedent(
                f"""
                The command syntax you used is incorrect. 
                **`{error}`**

                **Command Description**
                {command_help}

                **Command syntax**
                {command_syntax}

                Aliases: {aliases if aliases else None}
                """
            )
        )

    @classmethod
    def _get_missing_permission(cls, error) -> str:
        missing_perms = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_perms]

        if len(missing_perms) > 2:
            message = f"{'**, **'.join(missing_perms[:-1])}, and {missing_perms[-1]}"
        else:
            message = " and ".join(missing_perms)

        return message

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: errors.CommandError) -> None:
        """Handle all the errors occurring when running the bot."""
        if isinstance(error, errors.CommandNotFound):
            return
        
        elif isinstance(error, IncorrectChannelError):
            return

        elif isinstance(error, NoChannelProvided):
            await self.error_embed(ctx, 'You must be in a voice channel or provide one to connect to.')
            return

        elif isinstance(error, BotMissingPermissions):
            missing_perms = self._get_missing_permission(error)
            message = f"I need the **{missing_perms}** permission(s) to run this command."
            await self.error_embed(ctx, message)
            return

        elif isinstance(error, MissingPermissions):
            missing_perms = self._get_missing_permission(error)
            message = f"You need the **{missing_perms}** permission(s) to use this command."
            await self.error_embed(ctx, message)
            return

        elif isinstance(error, BotMissingRole):
            message = f"I need the **{error.missing_role}** role to run this command."
            await self.error_embed(ctx, message)
            return

        elif isinstance(error, MissingRole):
            message = f"You need the **{error.missing_role}** permission(s) to use this command."
            await self.error_embed(ctx, message)
            return

        elif isinstance(error, (CommandOnCooldown, MaxConcurrencyReached)):
            cooldowns = {
                BucketType.default: 'for the whole bot.',
                BucketType.user: 'for you.',
                BucketType.guild: 'for this server.',
                BucketType.channel: 'for this channel.',
                BucketType.member: 'cooldown for you.',
                BucketType.category: 'for this channel category.',
                BucketType.role: 'for your role.'
            }

            await self.error_embed(
                ctx,
                title="Command on cooldown",
                description=f'The command `{ctx.command}` is on cooldown {cooldowns[error.cooldown.type]} You can '
                            f'retry in `{format_time(error.retry_after)}`'
            )
            return

        elif isinstance(error, errors.UserInputError):
            await self.command_syntax_error(ctx, error)
            return

        elif isinstance(error, PrivateMessageOnly):
            await self.error_embed(
                ctx, description=f"❌ The command `{ctx.command}` can be used only in in private messages."
            )
            return

        elif isinstance(error, NoPrivateMessage):
            await self.error_embed(
                ctx, description=f"❌ The command `{ctx.command}` can not be used in private messages."
            )
            return

        elif isinstance(error, errors.CheckFailure):
            if isinstance(error, NotOwner):
                msg = "❌ This command is only for the bot owners."
            else:
                msg = "❌ You don't have enough permission to run this command."

            await self.error_embed(
                ctx,
                description=msg
            )
            return

        error_messages = {
            NSFWChannelRequired: f'The command `{ctx.command}` can only be ran in a NSFW channel.',
            DisabledCommand: f'The command `{ctx.command}` has been disabled.',
            ExpectedClosingQuoteError: f'You missed a closing quote in the parameters passed to the `{ctx.command}` '
                                       f'command.',
            UnexpectedQuoteError: f'There was an unexpected quote in the parameters passed to the `{ctx.command}` '
                                  f'command.',
            InvalidEndOfQuotedStringError: f"The quoted argument must be separated from the others with space in "
                                           f"`{ctx.command}`"
        }

        error_message = error_messages.get(type(error), None)
        if error_message is not None:
            await self.error_embed(
                ctx,
                title="Error",
                description=error_message
            )
            return

        elif isinstance(error, errors.CommandInvokeError):
            error_cause = error.__cause__

            if error_cause is not None:
                await self.error_embed(
                    ctx,
                    title="Unhandled Error",
                    description=textwrap.dedent(
                        f"""
                        An error has occurred which isn't properly handled.

                        **Error**
                        ```{error_cause.__class__.__name__}: {error_cause}```
                        """
                    )
                )
                logger.error(error_cause)
            return

        await self.error_embed(
            ctx,
            title="Unhandled exception",
            description=textwrap.dedent(
                f"""
                An error has occurred which isn't properly handled.

                **Error**
                ```{error.__class__.__name__}: {error}```
                """
            )
        )

        logger.error(error)
