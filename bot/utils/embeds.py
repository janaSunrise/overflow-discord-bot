import typing as t
from datetime import datetime
from textwrap import dedent

import discord
from discord.ext.commands import Context, MemberConverter

from bot.core.converters import ModerationReason


def moderation_embed(
    ctx: Context,
    action: str,
    user: t.Union[discord.Member, MemberConverter],
    reason: t.Union[str, ModerationReason],
    color: discord.Color = discord.Color.blue(),
) -> discord.Embed:
    """Return a quick embed for moderation event."""
    description = dedent(
        f"""
    User: {user.mention} [`{user.id}`]
    Reason Specified: {reason}

    Moderator: {ctx.author} [`{ctx.author.id}`]
    """
    )

    embed = discord.Embed(
        title=f"User {action}ed",
        description=description,
        color=color,
        timestamp=datetime.utcnow(),
    )
    return embed
