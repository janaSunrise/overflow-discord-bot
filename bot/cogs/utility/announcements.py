import discord
from discord.ext.commands import Cog, Context, group, has_permissions

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
    async def role(self, ctx: Context, role: discord.Role) -> None:
        """Setup the announcement role."""
        if isinstance(role, discord.Role):
            role = role.id

        await AnnouncementDB.set_announcement_role(self.bot.database, ctx.guild.id, role)

        role = ctx.guild.get_role(role)
        await ctx.send(f"The role has been successfully set to {role.mention}")

    @announcement.command()
    @has_permissions(manage_channels=True)
    async def channel(self, ctx: Context, channel: discord.TextChannel) -> None:
        """Setup the announcement role."""
        if isinstance(channel, discord.Role):
            channel = channel.id

        await AnnouncementDB.set_announcement_channel(self.bot.database, ctx.guild.id, channel)

        await ctx.send(f"The channel has been successfully set to {channel.mention}")

    @announcement.command()
    async def subscribe(self, ctx: Context) -> None:
        """Subscribe to the notifications and announcements in the server."""
        row = await AnnouncementDB.get_announcement_role(self.bot.database, ctx.guild.id)

        if not row:
            await ctx.send("The announcement role hasn't been configured for this server!")

        role = discord.utils.find(lambda r: r.id == row["role_id"], ctx.guild.roles)

        if role in ctx.author.roles:
            await ctx.send("You're already subscribed!")
        else:
            await ctx.author.add_roles(role)
            await ctx.send("Congrats 🎉! You're subscribed!")

    @announcement.command()
    async def unsubscribe(self, ctx: Context) -> None:
        """Unsubscribe from the notifications and announcements."""
        row = await AnnouncementDB.get_announcement_role(self.bot.database, ctx.guild.id)

        if not row:
            await ctx.send("ERROR! The Announcement role hasn't been configured for this server!")

        role = discord.utils.find(lambda r: r.id == row["role_id"], ctx.guild.roles)

        if role not in ctx.author.roles:
            await ctx.send("You're already unsubscribed!")
        else:
            await ctx.author.remove_roles(role)
            await ctx.send("Aww :( We hate to see you unsubscribe.")

