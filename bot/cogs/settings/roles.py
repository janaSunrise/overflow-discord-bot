import discord
from discord.ext.commands import (Cog, Context, RoleConverter, group,
                                  has_permissions)

from bot.databases.autorole import AutoRoles


class Roles(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @group(invoke_without_command=True)
    @has_permissions(manage_roles=True)
    async def autorole(self, ctx: Context) -> None:
        """Configuration settings for autorole."""
        row = await AutoRoles.get_roles(self.bot.database, ctx.guild.id)

        if row is not None:
            roles = row["auto_roles"]
            roles = "\n".join([f"• <@&{x}>" for x in roles])

            await ctx.send(
                embed=discord.Embed(
                    title="Autorole settings",
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
