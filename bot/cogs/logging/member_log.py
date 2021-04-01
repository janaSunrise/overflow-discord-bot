import textwrap
from datetime import datetime

import discord
from discord.ext.commands import Cog

from bot import Bot
from bot.databases.logging import Logging


class MemberLog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener("on_user_update")
    async def log_user_update(self, before: discord.User, after: discord.User) -> None:
        if before.name != after.name:
            embed = discord.Embed(
                title="Username change",
                description=textwrap.dedent(
                    f"""
                    **`Mention`**: {after.mention}
                    **`Old name`**: {before.name}
                    **`New name`**: {after.name}
                    """
                ),
                color=discord.Color.blue(),
            )
        elif before.discriminator != after.discriminator:
            embed = discord.Embed(
                title="Discriminator change",
                description=textwrap.dedent(
                    f"""
                    **`Mention`**: {after.mention}
                    **`Old Discriminator`**: {before.discriminator}
                    **`New Discriminator`**: {after.discriminator}
                    """
                ),
                color=discord.Color.blue(),
            )
        elif before.avatar != after.avatar:
            embed = discord.Embed(
                title="Avatar change",
                description=textwrap.dedent(
                    f"""
                    **`Mention`**: {after.mention}
                    **`Old avatar`**: [Old avatar]({before.avatar_url})
                    **`New avatar`**: [New avatar]({after.avatar_url})
                    """
                ),
                color=discord.Color.blue(),
            )

        embed.timestamp = datetime.utcnow()
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_footer(text=f"ID: {after.id}")

        member_logs = []
        for guild in self.bot.guilds:
            if guild.get_member(after.id) is None:
                continue

            member_log_channel_id = await Logging.get_config(
                self.bot.database, guild.id
            )
            member_log_channel = None

            if member_log_channel_id is not None:
                member_log_channel = guild.get_channel(
                    member_log_channel_id["member_log"]
                )

            if member_log_channel is not None:
                member_logs.append(member_log_channel)

        for channel in member_logs:
            await channel.send(embed=embed)

    async def send_member_log(self, guild: discord.Guild, *args, **kwargs) -> None:
        member_log_channel_id = await Logging.get_config(self.bot.database, guild.id)

        if not member_log_channel_id:
            return

        member_log_channel = guild.get_channel(
            member_log_channel_id["member_log"])

        if not member_log_channel:
            return

        await member_log_channel.send(*args, **kwargs)
