import typing as t
from collections import Counter
from datetime import datetime
from textwrap import dedent

import discord
import humanize
from discord.ext.commands import Cog, Context, MemberConverter, UserConverter, command

from bot import Bot


class Lookup(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.STATUSES = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫",
        }
        self.features = {
            "VIP_REGIONS": "Has VIP voice regions",
            "VANITY_URL": "Can have vanity invite",
            "INVITE_SPLASH": "Can have invite splash",
            "VERIFIED": "Is verified server",
            "PARTNERED": "Is partnered server",
            "MORE_EMOJI": "Can have 50+ emoji",
            "DISCOVERABLE": "Is discoverable",
            "FEATURABLE": "Is featurable",
            "COMMERCE": "Can have store channels",
            "PUBLIC": "Is public",
            "NEWS": "Can have news channels",
            "BANNER": "Can have banner",
            "ANIMATED_ICON": "Can have animated icon",
            "PUBLIC_DISABLED": "Can not be public",
            "WELCOME_SCREEN_ENABLED": "Can have welcome screen",
            "MEMBER_VERIFICATION_GATE_ENABLED": "Member verification enabled.",
            "PREVIEW_ENABLED": "Guild can be previewed.",
        }

    def get_user_embed(
        self, user: t.Union[UserConverter, MemberConverter]
    ) -> discord.Embed:
        """Create an embed with detailed info about given user"""
        embed = discord.Embed(
            title=f"{user}'s stats and information.", color=user.color
        )

        created_time = datetime.strftime(
            user.created_at, "%A %d %B %Y at %H:%M")

        # -- User info section --

        user_info = dedent(
            f"""
            Mention: {user.mention}

            Date Created: {created_time}
            Created time delta: {humanize.precisedelta(datetime.utcnow() - user.created_at, suppress=["seconds", "minutes"],
                                            format="%0.0f")} ago

            Is a bot: {str(user.bot).replace("True", "Yes").replace("False", "No")}
            Is pending verification: {str(user.pending).replace("True", "Yes").replace("False", "No")}
            """
        )

        # -- Server info section --

        if isinstance(user, discord.Member):
            member_info = ""

            if user.nick:
                member_info += f"Nickname: {user.nick}"

            joined_time = datetime.strftime(
                user.joined_at, "%A %d %B %Y at %H:%M")
            member_info += f"Joined server: {joined_time}"

            roles = [role.mention for role in user.roles[:10]]
            roles.reverse()

            member_info += f"\n\nTop Role: {user.top_role.mention}"

            roles = [f"• {role}" for role in roles]
            role_order = "\n".join(roles[:15])
            member_info += f"\nMain roles: \n{role_order}"

        else:
            member_info = (
                "No server related info, this user is not a member of this server."
            )

        # -- Status section --

        status_info = ""

        if not user.activity:
            status_info += "\nActivity: N/A"
        elif user.activity.type != discord.ActivityType.custom:
            status_info += f"\nActivity: {user.activity.type.name} {user.activity.name}"
        else:
            status_info += f"\nActivity: {user.activity.name}"

        try:
            status_info += f"\nStatus: {self.STATUSES[user.status]}"
        except KeyError:
            status_info += "\nStatus: N/A"

        if user.status == discord.Status.offline:
            status_info += "\nDevice: Unknown :no_entry:"
        elif user.is_on_mobile():
            status_info += "\nDevice: Phone :iphone:"
        else:
            status_info += "\nDevice: PC :desktop:"

        embed.add_field(name="❯ General information",
                        value=user_info, inline=False)
        embed.add_field(
            name="❯ Server related information", value=member_info, inline=False
        )
        embed.add_field(name="❯ Status information",
                        value=status_info, inline=True)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"UserID: {user.id}")

        return embed

    def get_server_embed(self, guild: discord.Guild) -> discord.Embed:
        """Get the information Embed from a guild."""
        region = (
            guild.region.name.title()
            .replace("Vip", "VIP")
            .replace("_", "-")
            .replace("Us-", "US-")
        )

        if guild.region == discord.VoiceRegion.hongkong:
            region = "Hong Kong"

        if guild.region == discord.VoiceRegion.southafrica:
            region = "South Africa"

        features = []
        for feature, description in self.features.items():
            if feature in guild.features:
                features.append(f"✅ | {description}")
            else:
                features.append(f"❌ | {description}")

        embed = discord.Embed(
            title=f"{guild.name}'s stats and information.",
            description=guild.description if guild.description else None,
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="❯ General information",
            value=dedent(
                f"""
                Name: {guild.name}
                Description: {guild.description}

                Created on: {datetime.strftime(guild.created_at, "%A %d %B %Y at %H:%M")}
                Created At: {humanize.precisedelta(datetime.utcnow() - guild.created_at, suppress=
                ["seconds", "minutes"], format="%0.0f")} ago

                Verification level: **{guild.verification_level}**

                Owner: <@!{guild.owner.id}>
                Member count: **`{guild.member_count}`**
                """
            ),
            inline=False,
        )

        embed.add_field(
            name="❯ Boost Info",
            value=dedent(
                f"""
                Nitro Tier: `{guild.premium_tier}`
                Boosters: `{guild.premium_subscription_count}`

                File Size: `{round(guild.filesize_limit / 1048576)}` MB
                Bitrate: `{round(guild.bitrate_limit / 1000)}` kbps

                Emoji: `{guild.emoji_limit}`
                Normal emoji: `{sum([1 for emoji in guild.emojis if not emoji.animated])}`
                Animated emoji: `{sum([1 for emoji in guild.emojis if emoji.animated])}`
                """
            ),
            inline=True,
        )
        embed.add_field(
            name="❯ Channels",
            value=dedent(
                f"""
                Text channels: `{len(guild.text_channels)}`
                Voice channels: `{len(guild.voice_channels)}`

                Voice region: {region}
                AFK timeout: `{round(guild.afk_timeout / 60)}`m | AFK channel: {None if guild.afk_channel is None else
                guild.afk_channel}
                """
            ),
            inline=True,
        )
        embed.add_field(
            name="❯ Features",
            value="\n".join(features),
            inline=False,
        )
        embed.set_thumbnail(url=guild.icon_url)
        embed.set_footer(text=f"Guild ID: {guild.id}")

        return embed

    @command(aliases=["server"])
    async def serverinfo(self, ctx: Context) -> None:
        """Get information about the server."""
        await ctx.send(embed=self.get_server_embed(ctx.guild))

    @command(aliases=["user"])
    async def userinfo(
        self,
        ctx: Context,
        user: t.Optional[t.Union[MemberConverter, UserConverter]] = None,
    ) -> None:
        """
        Get information about you, or a specified member.
        `user` can be a user Mention, Name, or ID.
        """
        if not user:
            user = ctx.author

        await ctx.send(embed=self.get_user_embed(user))

    @command()
    async def members(self, ctx: Context) -> None:
        """Get the number of members in the server."""
        member_by_status = Counter(str(m.status) for m in ctx.guild.members)
        bots = len([member for member in ctx.guild.members if member.bot])
        member_type = dedent(
            f"""
            Member count: {ctx.guild.member_count - bots}
            Bots count: {bots}
            """
        )
        status = dedent(
            f"""
            {self.STATUSES[discord.Status.online]} | **`{member_by_status["online"]}`**
            {self.STATUSES[discord.Status.idle]} | **`{member_by_status["idle"]}`**
            {self.STATUSES[discord.Status.dnd]} | **`{member_by_status["dnd"]}`**
            {self.STATUSES[discord.Status.offline]} | **`{member_by_status["offline"]}`**
            """
        )
        embed = discord.Embed(
            title="Member count",
            description=ctx.guild.member_count,
            color=discord.Color.blue(),
        )
        embed.add_field(name="❯ Member Status", value=status, inline=False)
        embed.add_field(name="❯ Member Type", value=member_type, inline=False)
        embed.set_author(name=f"Server : {ctx.guild.name}")

        await ctx.send(embed=embed)

    @command()
    async def icon(self, ctx: Context) -> None:
        """
        Displays a servers icon.
        `guild`: The server of which to get the icon for. Can be it's ID or Name. Defaults to the current server.
        """
        guild = ctx.guild

        if not guild.icon:
            await ctx.send(
                embed=discord.Embed(
                    description=f"The server `{guild}` does not have an icon.",
                    color=discord.Color.red(),
                )
            )
            return

        embed = discord.Embed(
            title=f"{guild.name}'s icon",
            description=f"""
               [PNG]({guild.icon_url_as(format="png")})
               [JPEG]({guild.icon_url_as(format="jpeg")})
               [WEBP]({guild.icon_url_as(format="webp")})
               """,
            color=discord.Color.blue(),
        )
        embed.set_image(url=str(guild.icon_url_as(format="png")))

        if guild.is_icon_animated():
            embed.description += f'\n[GIF]({guild.icon_url_as(format="gif")})'
            embed.set_image(
                url=str(guild.icon_url_as(size=1024, format="gif")))

        await ctx.send(embed=embed)

    @command()
    async def banner(self, ctx: Context) -> None:
        """
        Displays a servers banner.
        `guild`: The server of which to get the banner for. Can be it's ID or Name. Defaults to the current server.
        """
        guild = ctx.guild

        if not guild.banner:
            await ctx.send(
                embed=discord.Embed(
                    description=f"The server `{guild}` does not have an banner.",
                    color=discord.Color.red(),
                )
            )
            return

        embed = discord.Embed(
            title=f"{guild.name}'s banner",
            description=f"""
               [PNG]({guild.banner_url_as(format="png")})
               [JPEG]({guild.banner_url_as(format="jpeg")})
               [WEBP]({guild.banner_url_as(format="webp")})""",
            colour=discord.Color.blue(),
        )
        embed.set_image(url=str(guild.banner_url_as(format="png")))

        await ctx.send(embed=embed)
        return

    @command()
    async def splash(self, ctx: Context) -> None:
        """
        Displays a servers splash.
        `guild`: The server of which to get the splash for. Can be it's ID or Name. Defaults to the current server.
        """
        guild = ctx.guild

        if not guild.splash:
            await ctx.send(
                embed=discord.Embed(
                    description=f"The server `{guild}` does not have an splash icon.",
                    color=discord.Color.red(),
                )
            )
            return

        embed = discord.Embed(
            color=discord.Color.blurple(), title=f"{guild.name}'s splash"
        )
        embed.description = f"""
               [PNG]({guild.splash_url_as(format="png")})
               [JPEG]({guild.splash_url_as(format="jpeg")})
               [WEBP]({guild.splash_url_as(format="webp")})
           """
        embed.set_image(url=str(guild.splash_url_as(format="png")))

        return await ctx.send(embed=embed)
