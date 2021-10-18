import typing as t

import discord
from discord.ext.commands import (
    Cog,
    Context,
    RoleConverter,
    TextChannelConverter,
    group,
    has_permissions,
)

from bot import Bot
from bot.databases.announcements import Announcements as AnnouncementDB


class Announcements(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @property
    def embeds_cog(self) -> discord.Embed:
        """Get currently loaded Embed cog instance."""
        return self.bot.get_cog("Embeds")

    @group(invoke_without_command=True)
    async def announcement(self, ctx: Context) -> None:
        """Commands for hackernews and it's feeds."""
        await ctx.send_help(ctx.command)

    @announcement.command()
    @has_permissions(manage_roles=True)
    async def role(self, ctx: Context, role: RoleConverter) -> None:
        """Setup the announcement role."""
        await AnnouncementDB.set_announcement_role(
            self.bot.database, ctx.guild.id, role.id
        )

        await ctx.send(f"The role has been successfully set to {role.mention}")

    @announcement.command()
    @has_permissions(manage_channels=True)
    async def channel(self, ctx: Context, channel: TextChannelConverter) -> None:
        """Setup the announcement channel."""
        await AnnouncementDB.set_announcement_channel(
            self.bot.database, ctx.guild.id, channel.id
        )

        await ctx.send(f"The channel has been successfully set to {channel.mention}")

    @announcement.command()
    @has_permissions(manage_roles=True)
    async def announce(self, ctx: Context, *, message: t.Optional[str] = None) -> None:
        """
        Send a notification or announcement through the bot.

        This supports sending a simple message, or sending customized messages using our embed handler.
        """
        # -- Get the roles and IDs from database
        role = await AnnouncementDB.get_announcement_role(
            self.bot.database, ctx.guild.id
        )

        if not role["role_id"]:
            await ctx.send(
                "The announcement role hasn't been configured for this server!"
            )

        channel = await AnnouncementDB.get_announcement_channel(
            self.bot.database, ctx.guild.id
        )

        if not channel["channel_id"]:
            await ctx.send(
                "The announcement channel hasn't been configured for this server!"
            )

        # -- Get the embeds cog. --
        embed_data = self.embeds_cog.embeds[ctx.author.id]

        embed_message = embed_data.message
        embed = embed_data.embed

        # -- Get the discord objects --
        role = ctx.guild.get_role(role["role_id"])
        channel = ctx.guild.get_channel(channel["channel_id"])

        if not message and embed.description is None and embed.title is None:
            await ctx.send(
                ":x: You need to create an embed using our embed maker before sending it or specify a message!"
            )
            return

        if message is not None:
            if embed.title == discord.Embed.Empty:
                embed.title = "Announcement!"
            embed.description = message

        if embed_message == "" and embed == discord.Embed():
            message = f"Hey {role.mention}"
        else:
            msg = embed_message
            message = f"Hey {role.mention} {msg}"

        if not embed.footer:
            embed.set_footer(
                text=f"By {ctx.author.name}", icon_url=ctx.author.avatar_url
            )

        await channel.send(message, embed=embed)

    @announcement.command()
    async def subscribe(self, ctx: Context) -> None:
        """Subscribe to the notifications and announcements in the server."""
        row = await AnnouncementDB.get_announcement_role(
            self.bot.database, ctx.guild.id
        )

        if not row["role_id"]:
            await ctx.send(
                "The announcement role hasn't been configured for this server!"
            )

        role = discord.utils.find(lambda r: r.id == row["role_id"], ctx.guild.roles)

        if role in ctx.author.roles:
            await ctx.send("You're already subscribed!")
        else:
            await ctx.author.add_roles(role)
            await ctx.send("Congrats 🎉! You're subscribed!")

    @announcement.command()
    async def unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe from the notifications and announcements."""
        row = await AnnouncementDB.get_announcement_role(
            self.bot.database, ctx.guild.id
        )

        if not row:
            await ctx.send(
                "ERROR! The Announcement role hasn't been configured for this server!"
            )

        role = discord.utils.find(lambda r: r.id == row["role_id"], ctx.guild.roles)

        if role not in ctx.author.roles:
            await ctx.send("You're already unsubscribed!")
        else:
            await ctx.author.remove_roles(role)
            await ctx.send("Aww :( We hate to see you unsubscribe.")
