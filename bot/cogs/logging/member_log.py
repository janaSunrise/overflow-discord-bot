import textwrap
from datetime import datetime

import discord
from discord.ext.commands import Cog

from bot import Bot
from bot.databases.logging import Logging
from bot.utils.audit_log import get_latest_audit


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
        else:
            return

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

    @Cog.listener("on_member_update")
    async def log_member_update(
        self, before: discord.Member, after: discord.Member
    ) -> None:
        if before.nick != after.nick:
            embed = discord.Embed(
                title="Nickname change",
                description=textwrap.dedent(
                    f"""
                    **`Mention`**: {after.mention}
                    **`Old nickname`**: {before.nick}
                    **`New nickname`**: {after.nick}
                    """
                ),
                color=discord.Color.blue(),
            )
        elif before.pending != after.pending:
            embed = discord.Embed(
                title="Member verification completed",
                description=textwrap.dedent(
                    f"""
                    **`Mention`**: {after.mention}]
                    
                    User has passed the server verification.
                    """
                ),
                color=discord.Color.blue(),
            )
        elif before.roles != after.roles:
            new_roles = set(after.roles)
            old_roles = set(before.roles)

            stats = {"added": old_roles - new_roles, "removed": new_roles - old_roles}

            audit_log = await get_latest_audit(
                after.guild, [discord.AuditLogAction.member_role_update], after
            )

            if audit_log:
                user = audit_log.user

            action = "added" if not stats.get("removed") else "removed"

            description = textwrap.dedent(
                f"""
            **`Mention`**: {after.mention}
            **`Roles`**: {stats['removed'].pop().mention if stats['removed'] else stats['added'].pop().mention}
            """
            )

            if audit_log:
                description += f"\n**`Moderator`**: {user.mention}"

            embed = discord.Embed(
                title="Roles action",
                description=description,
                color=discord.Color.blue(),
            )

        else:
            return

        embed.timestamp = datetime.utcnow()
        embed.set_thumbnail(url=after.avatar_url)
        embed.set_footer(text=f"ID: {after.id}")

        await self.send_member_log(after.guild, embed=embed)

    async def send_member_log(self, guild: discord.Guild, *args, **kwargs) -> None:
        member_log_channel_id = await Logging.get_config(self.bot.database, guild.id)

        if not member_log_channel_id:
            return

        member_log_channel = guild.get_channel(member_log_channel_id["member_log"])

        if not member_log_channel:
            return

        await member_log_channel.send(*args, **kwargs)
