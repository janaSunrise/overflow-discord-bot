import textwrap

import discord
from discord.ext.commands import Cog, Context, TextChannelConverter, group

from bot import Bot
from bot.databases.suggestions import SuggestionConfig


class Suggestions(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(invoke_without_command=True)
    async def suggestion(self, ctx: Context):
        """Commands for suggestion config."""
        row = await SuggestionConfig.get_config(self.bot.database, ctx.guild.id)

        if not row:
            await ctx.send("⚠️Suggestion channel not configured!")
            return

        await ctx.send(
            embed=discord.Embed(
                title="Suggestion settings configuration",
                description=textwrap.dedent(
                    f"""
                    • Channel: {f"<#{row['channel_id']}>"}
                    • Submission Channel: {
                        f"<#{row['submission_channel_id']}>" if row["submission_channel_id"] is not None else 
                        "No channel configured!"
                    }
                    • Limit: {row["limit"]}
                    • DM on decision: {row["dm_notification"]}
                    • Anonymous suggestions: {row["anonymous"]} 
                    """
                ),
                color=discord.Color.blue(),
            )
        )

    @suggestion.command()
    async def channel(self, ctx: Context, channel: TextChannelConverter) -> None:
        """Register a channel as a suggestion channel."""
        await SuggestionConfig.set_suggestions_channel(
            self.bot.database, ctx.guild.id, channel.id
        )
        await ctx.send(f"Set suggestion channel to {channel.mention}")

    @suggestion.command()
    async def submission_channel(self, ctx: Context, channel: TextChannelConverter) -> None:
        """Register a channel as a submission channel where people can suggest."""
        await SuggestionConfig.set_submission_channel(
            self.bot.database, ctx.guild.id, channel.id
        )
        await ctx.send(f"Set submission channel to {channel.mention}")

    @suggestion.command()
    async def limit(self, ctx: Context, limit: int) -> None:
        """Set the limit for the starboard."""
        if limit <= 0:
            await ctx.send("❌ Invalid limit specified.")
            return

        await SuggestionConfig.set_limit(
            self.bot.database, ctx.guild.id, limit
        )
        await ctx.send(f"Set limit to {limit}")
