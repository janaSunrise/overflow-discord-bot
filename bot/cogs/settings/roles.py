import textwrap

import discord
from discord.ext.commands import Cog, Context, RoleConverter, group, has_permissions

from bot import Bot
from bot.databases.autorole import AutoRoles
from bot.databases.roles import Roles as RolesDB


class Roles(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(
        invoke_without_command=True, aliases=["role-config", "role-conf", "role-cfg"]
    )
    @has_permissions(manage_roles=True)
    async def role_config(self, ctx: Context) -> None:
        """Role configuration settings for a guild."""
        row = await RolesDB.get_roles(self.bot.database, ctx.guild.id)

        if row is not None:
            mute_role = ctx.guild.get_role(row["mute_role"])
            default_role = ctx.guild.get_role(row["default_role"])

            if not default_role:
                await RolesDB.set_role(self.bot.database, "default_role", ctx.guild, ctx.guild.default_role.id)

            mod_role = "\n".join([f"• <@&{x}>" for x in row["mod_role"]])

            await ctx.send(
                embed=discord.Embed(
                    title="Role settings configuration",
                    description=textwrap.dedent(
                        f"""
                        ❯ **Moderator roles:**
                        {mod_role}
                        
                        ❯ Mute role: {mute_role.mention}
                        ❯ Default role: {default_role.mention}
                        """
                    ),
                    color=discord.Color.blue(),
                )
            )
        else:
            await ctx.send("No role configuration is added for this guild.")

    @role_config.command()
    async def default(self, ctx: Context, role: RoleConverter = None) -> None:
        """Configure the default role for this server. If left empty, `@everyone` is configured as the default role."""
        if not role:
            role = ctx.guild.default_role

        await RolesDB.set_role(self.bot.database, "default_role", ctx.guild, role.id)
        await ctx.send("Successfully configured the default role.")

    @role_config.command()
    async def mute(self, ctx: Context, role: RoleConverter = None) -> None:
        """Configure the muted role for the server."""
        if not role:
            await ctx.send(":x: Specify a role to configured as the mute role.")

        await RolesDB.set_role(self.bot.database, "mute_role", ctx.guild, role.id)
        await ctx.send("Successfully configured the mute role.")

    @role_config.command(aliases=["mod", "staff"])
    async def moderator(self, ctx: Context, role: RoleConverter = None) -> None:
        """Configure the muted role for the server."""
        if not role:
            await ctx.send(":x: Specify a role to configured as the moderator role.")

        await RolesDB.set_role(self.bot.database, "mod_role", ctx.guild, [role.id])
        await ctx.send("Successfully configured the moderator role.")

    @group(invoke_without_command=True)
    @has_permissions(manage_roles=True)
    async def autorole(self, ctx: Context) -> None:
        """Configuration settings for autorole."""
        row = await AutoRoles.get_roles(self.bot.database, ctx.guild.id)

        if row is not None and row["auto_roles"] != []:
            roles = row["auto_roles"]
            roles = "\n".join([f"• <@&{x}>" for x in roles])

            await ctx.send(
                embed=discord.Embed(
                    title="Autorole configuration settings",
                    description=f"Roles configured for autorole:\n{roles}",
                    color=discord.Color.green(),
                )
            )
        else:
            await ctx.send("This server doesn't assign any roles upon joining.")

    @autorole.command()
    async def add(self, ctx: Context, role: RoleConverter = None) -> None:
        """Add a role to the autorole list."""
        if not role:
            await ctx.send(":x: Specify a role to be added to the autorole list.")

        row = await AutoRoles.get_roles(self.bot.database, ctx.guild.id)

        roles = []
        if row is not None:
            roles += row["auto_roles"]

        if role.id not in roles:
            roles.append(role.id)
            await AutoRoles.set_role(self.bot.database, ctx.guild.id, roles)
            await ctx.send(f"{role.mention} will be now auto assigned.")
        else:
            await ctx.send("Role already in the autorole list.")

    @autorole.command()
    async def remove(self, ctx: Context, role: RoleConverter = None) -> None:
        """Add a remove to the autorole list."""
        if not role:
            await ctx.send(":x: Specify a role to be removed from the autorole list.")

        row = await AutoRoles.get_roles(self.bot.database, ctx.guild.id)

        roles = []
        if row is not None:
            roles += row["auto_roles"]

        if role.id in roles:
            roles.remove(role.id)
            await AutoRoles.set_role(self.bot.database, ctx.guild.id, roles)
            await ctx.send(f"{role.mention} will not be auto assigned anymore.")
        else:
            await ctx.send("Role is not in the autorole list.")

    @autorole.command()
    async def clear(self, ctx: Context, role: RoleConverter = None) -> None:
        """Remove all the autoroles configured."""
        await AutoRoles.set_role(self.bot.database, ctx.guild.id, [])
        await ctx.send(f"Autoroles list cleared.")
