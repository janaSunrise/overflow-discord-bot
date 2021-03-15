import textwrap

import discord
from discord.ext.commands import (Cog, Context, group, guild_only,
                                  has_permissions)

from bot import Bot
from bot.databases.mod_lock import ModLock as ModLockDB


class ModerationLock(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener("on_member_join")
    async def apply_lock(self, member: discord.Member) -> None:
        """Apply the lock status if there is one."""
        status = await self.get_lock(member.guild.id)

        if status == 2:
            await member.ban(reason="Automod ban lock")

        elif status == 1:
            await member.kick(reason="Automod kick lock")

    async def get_lock(self, guild_id: int) -> int:
        """Ensure that the given guild_id is in the database."""
        row = await ModLockDB.get_config(self.bot.database, guild_id=guild_id)

        if not row:
            return 0
        return row["lock_code"]

    @group(invoke_without_command=True, name="mod-lock")
    @has_permissions(ban_members=True)
    @guild_only()
    async def mod_lock(self, ctx: Context) -> None:
        """Set the mod lock mode."""
        lock_mode = await self.get_lock(ctx.guild.id)

        mapping = {0: "❌ No lock", 1: "⚙️Kick lock enabled",
                   2: "⚙️Ban lock enabled"}

        await ctx.send(
            embed=discord.Embed(
                title="Mod lock settings configuration",
                description=textwrap.dedent(
                    f"""
                    • LOCK ENABLED: **`{True if lock_mode == 0 else False}`**
                    • Lock type: **`{mapping[lock_mode]}`**
                    """
                ),
                color=discord.Color.blue(),
            )
        )

    @mod_lock.command()
    async def unlock(self, ctx: Context) -> None:
        """Unlock the server."""
        status = await self.get_lock(ctx.guild.id)

        if status == 0:
            embed = discord.Embed(
                description="❌ The server is already unlocked!",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        await ModLockDB.set_lock(self.bot.database, ctx.guild.id, 0)
        embed = discord.Embed(
            description="Server Locks Are Successfully Disabled! You can now invite your friends and everyone!",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)

    @mod_lock.command()
    async def kick(self, ctx: Context) -> None:
        """Kick all new members."""
        status = await self.get_lock(ctx.guild.id)

        if status:
            lock_type = "Kick" if status == 1 else "Ban"
            embed = discord.Embed(
                title="Server Lock Error!",
                description=(
                    f"⚠️ {lock_type} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}mod-lock unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        await ModLockDB.set_lock(self.bot.database, ctx.guild.id, 1)
        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Kick Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users joining while the lock is on will be kicked until it is lifted.
            """
        )
        embed = discord.Embed(
            title="Server Lock Enabled", description=desc, color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @mod_lock.command()
    async def ban(self, ctx: Context) -> None:
        """Ban all new members."""
        status = await self.get_lock(ctx.guild.id)

        if status:
            lock_status = "Kick" if status == 1 else "Ban"
            embed = discord.Embed(
                title="Server Lock Error!",
                description=(
                    f"⚠️ {lock_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}mod-lock unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        await ModLockDB.set_lock(self.bot.database, ctx.guild.id, 2)
        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Ban Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users joining while the lock is on will be banned until it is lifted.
            """
        )
        embed = discord.Embed(
            title="Server Lock Enabled", description=desc, color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
