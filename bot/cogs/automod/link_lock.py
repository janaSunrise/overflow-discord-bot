import re
import textwrap
import typing as t

import discord
from discord.ext.commands import Cog, Context, group, guild_only, has_permissions

from bot import Bot
from bot.databases.link_lock import LinkLock as LinkLockDB


class LinkLock(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.lock_map = {
            1: "Discord Invite",
            2: "Link lock excluding discord invite",
            3: "Link and discord invite lock",
        }

        self.link_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\
        ([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.invite_regex = (
            r"(?:discord(?:[\.,]|dot)gg|discord(?:[\.,]|dot)com(?:\/|slash)invite|"
            r"discordapp(?:[\.,]|dot)com(?:\/|slash)invite|discord(?:[\.,]|dot)me|"
            r"discord(?:[\.,]|dot)io)(?:[\/]|slash)([a-zA-Z0-9\-]+)"
        )

    def get_codes(self, string: str) -> t.List[str]:
        """Get the invite codes codes from a link."""
        return re.findall(self.invite_regex, string)

    @staticmethod
    async def is_our_invite(fragment: str, guild: discord.Guild) -> bool:
        """Check if the invite code is an invite for the given guild."""
        return fragment in [invite.code for invite in await guild.invites()]

    @Cog.listener("on_message")
    async def apply_link(self, message: discord.Message) -> None:
        """Apply the link_lock status."""
        status = await self.get_link(message.guild.id)

        if status == 1:
            for code in self.get_codes(message.content):
                if not await self.is_our_invite(code, message.guild):
                    await message.channel.send(
                        f"{message.author.mention}, you are not allowed to post other servers' invites!"
                    )
                    await message.delete()
            return

        if status == 2:
            for code in self.get_codes(message.content):
                if not await self.is_our_invite(code, message.guild):
                    return

            if re.findall(
                self.link_regex,
                message.content,
            ):
                await message.channel.send(
                    f"{message.author.mention}, you are not allowed to post any links here!"
                )
                await message.delete()

            return

        if status == 3:
            if re.findall(
                self.link_regex,
                message.content,
            ):
                for code in self.get_codes(message.content):
                    if not await self.is_our_invite(code, message.guild):
                        await message.channel.send(
                            f"{message.author.mention}, you are not allowed to post any links here!"
                        )
                        await message.delete()
            return

    async def get_link(self, guild_id: int) -> int:
        """Ensure that the given guild_id is in the database."""
        row = await LinkLockDB.get_config(self.bot.database, guild_id=guild_id)

        if not row:
            return 0
        return row["lock_code"]

    @group(invoke_without_command=True, name="link-lock")
    @has_permissions(ban_members=True)
    @guild_only()
    async def link_lock(self, ctx: Context) -> None:
        """Set the mod lock mode."""
        lock_mode = await self.get_link(ctx.guild.id)

        mapping = {
            0: "❌ No lock",
            1: "⚙️Invite lock enabled",
            2: "⚙️Link lock enabled[excluding discord invites]",
            3: "⚙ Link and invite lock enabled.",
        }

        await ctx.send(
            embed=discord.Embed(
                title="Link lock settings configuration",
                description=textwrap.dedent(
                    f"""
                        • LOCK ENABLED: **`{False if lock_mode == 0 else True}`**
                        • Lock type: **`{mapping[lock_mode]}`**
                        """
                ),
                color=discord.Color.blue(),
            )
        )

    @link_lock.command()
    async def link(self, ctx: Context) -> None:
        """Prevent everybody from posting links."""
        status = await self.get_link(ctx.guild.id)

        if status:
            link_status = self.lock_map[status]

            embed = discord.Embed(
                title="Link Lock Error!",
                description=(
                    f"⚠️ {link_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}link-lock unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        await LinkLockDB.set_lock(self.bot.database, ctx.guild.id, 2)
        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Discord Link Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: No user can now post any link on the server.
            """
        )
        embed = discord.Embed(
            title="Link Lock Enabled", description=desc, color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @link_lock.command()
    async def invite(self, ctx: Context) -> None:
        """Prevent everybody from posting other server's invites."""
        status = await self.get_link(ctx.guild.id)

        if status:
            link_status = self.lock_map[status]

            embed = discord.Embed(
                title="Link Lock Error!",
                description=(
                    f"⚠️ {link_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}link-lock unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        await LinkLockDB.set_lock(self.bot.database, ctx.guild.id, 1)
        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Discord Invite Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users sending other servers' invited's messages will be removed and warned.
            """
        )
        embed = discord.Embed(
            title="Link Lock Enabled", description=desc, color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @link_lock.command()
    async def link_invite(self, ctx: Context) -> None:
        """Prevent everybody from posting other server's invites and also all links."""
        status = await self.get_link(ctx.guild.id)

        if status:
            link_status = self.lock_map[status]

            embed = discord.Embed(
                title="Link Lock Error!",
                description=(
                    f"⚠️ {link_status} Lock is already "
                    "enabled on this server! Please use "
                    f"**`{ctx.prefix}link-lock unlock`** to lift this lock!"
                ),
            )
            await ctx.send(embed=embed)
            return

        await LinkLockDB.set_lock(self.bot.database, ctx.guild.id, 3)
        desc = textwrap.dedent(
            f"""
            **Lock type**: ⚙️Link and Discord Invite Lock
            **Enabler**: {ctx.author.mention}
            **INFO**: All users sending links or other servers' invited's messages will be removed and warned.
            """
        )
        embed = discord.Embed(
            title="Link Lock Enabled", description=desc, color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @link_lock.command()
    async def unlock(self, ctx: Context) -> None:
        """Allow posting links."""
        status = await self.get_link(ctx.guild.id)

        if status == 0:
            embed = discord.Embed(
                description="⚠️ Link Lock is already disabled on this server!",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return

        await LinkLockDB.set_lock(self.bot.database, ctx.guild.id, 0)
        embed = discord.Embed(
            description="Link Locks Are Successfully Disabled! You can now send links!",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed)
