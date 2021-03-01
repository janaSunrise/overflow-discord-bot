import discord
from discord.ext.commands import Cog
from loguru import logger

from bot import Bot
from bot.databases.autorole import AutoRoles


class Events(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Log message on guild join."""
        logger.info(f"[GUILD] Joined {guild.name}")

    @Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Log message on guild remove."""
        logger.info(f"[GUILD] Left {guild.name}")

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        # Ignore if the member is a bot.
        if member.bot:
            return

        guild = member.guild

        row = await AutoRoles.get_roles(self.bot.database, guild.id)

        if row is not None and row["auto_roles"] != []:
            roles = row["auto_roles"]

            for role in roles:
                role_obj = await guild.get_role(role)

                if not role_obj:
                    continue
                await member.add_roles(role)
        else:
            return
