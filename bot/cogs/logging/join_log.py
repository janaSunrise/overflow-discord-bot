import textwrap
from datetime import datetime

import discord
from discord.ext.commands import Cog

from bot import Bot
from bot.databases.logging import Logging
from bot.utils.time import time_ago


class JoinLog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener("on_member_join")
    async def member_join_log(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Member joined",
            description=textwrap.dedent(
                f"""
                **`Member`**: {member.mention}
                **`Member Count`**: {member.guild.member_count}
                **`Created at`**: {time_ago(member.created_at)}
                """
            ),
            color=discord.Color.blue(),
        )
        embed.set_author(name=member.name)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Member ID: {member.id}")
        embed.timestamp = datetime.utcnow()
        
        await self.send_join_log(member.guild, embed=embed)

    @Cog.listener("on_member_remove")
    async def member_leave_log(self, member: discord.Member) -> None:
        embed = discord.Embed(
            title="Member left",
            description=textwrap.dedent(
                f"""
                **`Member`**: {member.mention}
                **`Member Count`**: {member.guild.member_count}
                **`Joined at`**: {time_ago(member.joined_at)}
                **`Roles`**: {", ".join(role.mention for role in member.roles[1:])}
                """
            ),
            color=discord.Color.gold(),
        )
        embed.set_author(name=member.name)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Member ID: {member.id}")
        embed.timestamp = datetime.utcnow()

        await self.send_join_log(member.guild, embed=embed)

    async def send_join_log(self, guild: discord.Guild, *args, **kwargs) -> None:
        join_log_channel_id = await Logging.get_config(self.bot.database, guild.id)
        join_log_channel = guild.get_channel(join_log_channel_id["join_log"])

        if not join_log_channel:
            return

        await join_log_channel.send(*args, **kwargs)
