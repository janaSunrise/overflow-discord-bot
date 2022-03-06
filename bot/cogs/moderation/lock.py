import discord
from discord.ext.commands import (
    Cog,
    Context,
    Greedy,
    NoPrivateMessage,
    RoleConverter,
    TextChannelConverter,
    command,
    has_permissions,
)

from bot import Bot
from bot.databases.roles import Roles as RolesDB


class Lock(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    def cog_check(self, ctx: Context) -> bool:
        if ctx.guild:
            return True

        raise NoPrivateMessage

    async def get_default_role(self, ctx: Context) -> discord.Role:
        row = await RolesDB.get_roles(self.bot.database, ctx.guild.id)
        if row is not None and row["default_role"] is not None:
            default_role = ctx.guild.get_role(row["default_role"])
        else:
            default_role = ctx.guild.default_role

        return default_role

    @command()
    @has_permissions(manage_channels=True)
    async def lock(
        self,
        ctx: Context,
        channels: Greedy[TextChannelConverter] = None,
        override_roles: Greedy[RoleConverter] = None,
    ) -> None:
        """
        Lock a channel to stop people from talking and make the server under maintenance.

        Specify the override roles so that the specified roles can talk.
        """
        default_role = await self.get_default_role(ctx)

        guild = ctx.guild

        if not channels:
            channels = [ctx.channel]

        overwrites = {
            default_role: discord.PermissionOverwrite(send_messages=False),
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
        channels: Greedy[TextChannelConverter] = None,
        override_roles: Greedy[RoleConverter] = None,
    ) -> None:
        """
        Unlock a locked channel to continue traffic.

        Specify the override roles so that the specified roles cannot talk.
        """
        default_role = await self.get_default_role(ctx)
        guild = ctx.guild
        if not channels:
            channels = [ctx.channel]

        overwrites = {
            default_role: discord.PermissionOverwrite(send_messages=True),
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
                f"Unlocked {channel_count} channel{'s' if channel_count > 1 else ''}."
            )

    @command()
    @has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx: Context,
        duration: int = 0,
        channels: Greedy[TextChannelConverter] = None,
    ) -> None:
        """
        Set slowmode in 1 or more channel.

        Specify the duration for slowmode, or just execute the command without adding anything to remove the slowmode.
        """
        if not 0 <= duration <= 60 * 60 * 6:
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

    @command(name="maintenance-lock", aliases=["maintenancelock", "m-lock"])
    @has_permissions(administrator=True)
    async def maintenance_lock(
        self, ctx: Context, override_roles: Greedy[RoleConverter] = None
    ) -> None:
        """
        Disable default role's permission to send message on all channels.

        Specify the override roles so that the specified roles can talk or connect to VC.
        """
        channel_count = 0
        default_role = await self.get_default_role(ctx)
        guild = ctx.guild

        overwrites = {
            default_role: discord.PermissionOverwrite(
                send_messages=False, connect=False
            ),
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
                overwrites[role] = discord.PermissionOverwrite(
                    send_messages=True, connect=True
                )

        for channel in ctx.guild.channels:
            await channel.edit(
                overwrites=overwrites,
                reason=f"Reason: Server Under Maintenance | Requested by {ctx.author}.",
            )
            channel_count += 1

        await ctx.send(
            f"Locked down {channel_count} channel{'s' if channel_count > 1 else ''}. Server Under Maintenance."
        )

    @command(name="maintenance-unlock", aliases=["maintenanceunlock", "m-unlock"])
    @has_permissions(administrator=True)
    async def maintenance_unlock(
        self, ctx: Context, override_roles: Greedy[RoleConverter] = None
    ) -> None:
        """
        Enable default role's permission to send message on all channels.

        Specify the override roles so that the specified roles can talk or connect to VC.
        """
        channel_count = 0
        default_role = await self.get_default_role(ctx)
        guild = ctx.guild

        overwrites = {
            default_role: discord.PermissionOverwrite(send_messages=True, connect=True),
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
                overwrites[role] = discord.PermissionOverwrite(
                    send_messages=False, connect=False
                )

        for channel in ctx.guild.channels:
            await channel.edit(
                overwrites=overwrites,
                reason=f"Reason: Server Maintenance Lifted | Requested by {ctx.author}.",
            )
            channel_count += 1

        await ctx.send(
            f"Unlocked {channel_count} channel{'s' if channel_count > 1 else ''}. Server Maintenance lifted."
        )
