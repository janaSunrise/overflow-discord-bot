import discord


def moderation_embed(description: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Return a quick embed for moderation event."""
    return discord.Embed(description=description, color=color)
