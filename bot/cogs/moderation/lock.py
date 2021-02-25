import discord
from discord.ext.commands import (Cog, Context, Greedy, NoPrivateMessage,
                                  command, has_permissions)

from bot import Bot


class Lock(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def cog_check(self, ctx: Context):
        if ctx.guild:
            return True

        raise NoPrivateMessage

    @command()
    @has_permissions(manage_channels=True)
    async def lock(
        self,
        ctx: Context,
        channels: Greedy[discord.TextChannel] = None,
        override_roles: Greedy[discord.Role] = None,
    ) -> None:
        """
        Lock a channel to stop people from talking and make the server under maintenance.

        Specify the override roles so that the specified roles can talk.
        """
        guild = ctx.guild

        if not channels:
            channels = [ctx.channel]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                add_reactions=True,
                manage_channels=True,
            ),
        }

        if override_roles is not None:
            for role in override_roles:
                role = discord.utils.get(guild.roles, id=role.id)
                overwrites[role] = discord.PermissionOverwrite(
                    send_messages=True,
                )

        channel_count = 0
        for channel in channels:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.edit(overwrites=overwrites)
                channel_count += 1

                await channel.send("🔒 Locked down this channel.")
            else:
                continue

        if channels != [ctx.channel]:
            await ctx.send(
                f"Locked down {channel_count} channel{'s' if channel_count > 1 else ''}."
            )

    @command()
    @has_permissions(manage_channels=True)
    async def unlock(
        self,
        ctx: Context,
        channels: Greedy[discord.TextChannel] = None,
        override_roles: Greedy[discord.Role] = None,
    ) -> None:
        """
        Unlock a locked channel to continue traffic.

        Specify the override roles so that the specified roles cannot talk.
        """
        guild = ctx.guild

        if not channels:
            channels = [ctx.channel]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=True),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                add_reactions=True,
                manage_channels=True,
            ),
        }

        if override_roles is not None:
            for role in override_roles:
                role = discord.utils.get(guild.roles, id=role.id)
                overwrites[role] = discord.PermissionOverwrite(
                    send_messages=False,
                )

        channel_count = 0
        for channel in channels:
            if channel.permissions_for(ctx.author).manage_channels:
                await channel.edit(overwrites=overwrites)
                channel_count += 1

                await channel.send("🔓 Unlocked down this channel.")
            else:
                continue

        if channels != [ctx.channel]:
            await ctx.send(
                f"Locked down {channel_count} channel{'s' if channel_count > 1 else ''}."
            )

    @command()
    @has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx: Context,
        duration: int = 0,
        channels: Greedy[discord.TextChannel] = None,
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
                    color=discord.Color.red(),
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
            await ctx.send(
                f"✅ Disabled slowmode for {channel_count} channel{'s' if channel_count > 1 else ''}."
            )
