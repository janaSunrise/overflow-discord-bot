import discord
from discord.ext import commands

from bot import Bot


class Lock(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        if ctx.guild:
            return True

        raise commands.NoPrivateMessage

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(
            self,
            ctx: commands.Context,
            channels: commands.Greedy[discord.TextChannel] = None,
    ) -> None:
        if not channels:
            channels = [ctx.channel]

        channel_count = 0
        for channel in channels:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.set_permissions(channel.guild.default_role, send_messages=False)
                channel_count += 1
            else:
                continue
            await channel.send("🔒 Locked down this channel.")

        if channels != [ctx.channel]:
            await ctx.send(f"Locked down {channel_count} channel{'s' if channel_count > 1 else ''}.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(
            self, ctx: commands.Context, duration: int = 0, channels: commands.Greedy[discord.TextChannel] = None
    ) -> None:
        """
        Set slowmode in 1 or more channel.

        Specify the duration for slowmode, or just execute the command without adding anything to remove the slowmode.
        """
        if not 0 <= duration <= 21600:
            await ctx.send(
                embed=discord.Embed(
                    description=":x: The duration specified is out of bounds. Minimum 0 to remove slowmode "
                                "or 21600 for 6 hours slowmode.",
                    color=discord.Color.red()
                )
            )

        if channels is None:
            channels = [ctx.channel]

        channel_count = 0
        for channel in channels:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.edit(slowmode_delay=duration)
                channel_count += 1
            else:
                continue

        if duration != 0:
            await ctx.send(
                f"✅ Set {channel_count} channel{'s' if channel_count > 1 else ''} with {duration} second slowmode."
                )
        else:
            await ctx.send(f"✅ Disabled slowmode for {channel_count} channel{'s' if channel_count > 1 else ''}.")
