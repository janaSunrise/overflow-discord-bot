from datetime import datetime
from textwrap import dedent

import discord
from discord.ext import commands


def moderation_embed(
        ctx: commands.Context,
        action: str,
        user: discord.Member,
        reason: str,
        color: discord.Color = discord.Color.blue()
) -> discord.Embed:
    """Return a quick embed for moderation event."""
    description = dedent(f"""
    User: {user} [`{user.id}`]
    Reason Specified: {reason}
    
    Moderator: {ctx.author} [`{ctx.author.id}`]
    """)

    embed = discord.Embed(
        title=f"User {action}",
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    return embed
