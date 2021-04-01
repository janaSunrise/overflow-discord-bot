import discord
from discord.ext.commands import Cog

from bot import Bot
from bot.databases.logging import Logging


class VoiceLog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener("on_voice_state_update")
    async def voice_log(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        print(f"Mute: {before.mute} | {after.mute}")

        if before.mute != after.mute:
            embed = discord.Embed(
                title="User muted" if after.mute else "User un-muted",
                description=f"**`User`**: {member.mention}",
                color=discord.Color.gold()
            )
        elif before.deaf != after.deaf:
            embed = discord.Embed(
                title="User deafened" if after.mute else "User un-deafened",
                description=f"**`User`**: {member.mention}",
                color=discord.Color.gold()
            )
        elif before.afk != after.afk:
            embed = discord.Embed(
                title="User is now AFK" if after.afk else "User is not AFK Anymore",
                description=f"**User:** {member.mention}",
                color=discord.Color.gold()
            )
        elif before.channel != after.channel:
            description = f"**User**: {member.mention}"

            if after.channel:
                description += f"\n**After Channel**: {after.channel}"

            if before.channel:
                description += f"\n**Before Channel**: {before.channel}"

            embed = discord.Embed(
                title="Channels switched" if after.channel else "Voice channel disconnected",
                description=description,
                color=discord.Color.gold()
            )
        else:
            return

        embed.set_thumbnail(url=member.avatar_url)

        await self.send_voice_log(member.guild, embed=embed)

    async def send_voice_log(self, guild: discord.Guild, *args, **kwargs) -> None:
        voice_log_channel_id = await Logging.get_config(self.bot.database, guild.id)
        voice_log_channel = guild.get_channel(voice_log_channel_id["voice_log"])

        if not voice_log_channel:
            return

        await voice_log_channel.send(*args, **kwargs)
