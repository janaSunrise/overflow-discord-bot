import typing as t
from collections import defaultdict, namedtuple

import discord
from discord.ext.commands import (Cog, ColorConverter, Context,
                                  MessageConverter, group)

from bot import Bot

EmbedInfo = namedtuple("EmbedInfo", ("message", "embed"))


class Embeds(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.embeds = defaultdict(lambda: EmbedInfo("", discord.Embed()))

    @group(invoke_without_command=True)
    async def embed(self, ctx: Context) -> None:
        """Commands to create amazing customizable embeds in an easy way."""
        await ctx.send_help(ctx.command)

    @embed.command()
    async def show(self, ctx: Context) -> None:
        """Show your embed, how it looks before using it."""
        await ctx.send(
            self.embeds[ctx.author.id].message, embed=self.embeds[ctx.author.id].embed
        )

    @embed.command()
    async def reset(self, ctx: Context) -> None:
        """Reset your created embed."""
        self.embeds[ctx.author.id] = EmbedInfo("", discord.Embed())
        await ctx.send("✅ Your embed was successfully reset.")

    @embed.command(name="import", aliases=["import-embed"])
    async def import_(self, ctx: Context, message: MessageConverter) -> None:
        self.embeds[ctx.author.id] = EmbedInfo(
            message.content if message.content is not None else "", message.embeds[0]
        )

        await ctx.send("✅ Successfully import the specified embed / message.")

    @embed.command()
    async def send(self, ctx: Context, channel: discord.TextChannel) -> None:
        """Send your created embed to the specified channel."""
        can_send_message = channel.permissions_for(ctx.author).send_messages

        if can_send_message:
            await channel.send(
                self.embeds[ctx.author.id].message,
                embed=self.embeds[ctx.author.id].embed,
            )
            await ctx.send(f"✅ Your embed was successfully sent to {ctx.channel}")
        else:
            await ctx.send(
                f"❌ You need the permissions to send messages in {channel.mention}"
            )

    @embed.command()
    async def title(self, ctx: Context, *, title: str) -> None:
        """Set the title field for your embed."""
        self.embeds[ctx.author.id].embed.title = title
        await ctx.send(f"✅ Set title to `{title}`.")

    @embed.command(name="description")
    async def description_(self, ctx: Context, *, description: str) -> None:
        """Set description for your embed."""
        self.embeds[ctx.author.id].embed.description = description
        await ctx.send("✅ Set the description successfully.")

    @embed.command()
    async def color(self, ctx: Context, color: ColorConverter) -> None:
        """Add colors to make your embed better!"""
        self.embeds[ctx.author.id].embed.color = color
        await ctx.send(f"✅ Set color to `{color}`")

    @embed.command()
    async def footer(self, ctx: Context, *, footer_text: str) -> None:
        """Set the footer message for your embed."""
        self.embeds[ctx.author.id].embed.set_footer(text=footer_text)
        await ctx.send("✅ Successfully set the footer.")

    @embed.command()
    async def image(self, ctx: Context, image_url: str = None) -> None:
        """Set the image for your embed. It can be an attachment or an URL."""
        clean_image_extension = ["jpg", "jpeg", "png", "bmp"]

        if image_url is not None:
            self.embeds[ctx.author.id].embed.set_image(url=image_url)
        elif ctx.message.attachments:
            attachment = ctx.message.attachments[0]

            extension = attachment.filename.lower().split(".")[1]
            if extension not in clean_image_extension:
                await ctx.send("❌ Invalid image extension to parse.")
                return
            else:
                self.embeds[ctx.author.id].embed.set_image(url=attachment.url)
        else:
            await ctx.send(
                "❌ Please supply an URL or upload an image to add to the embed."
            )
            return

        await ctx.send("✅ Successfully set the image.")

    @embed.command()
    async def message(self, ctx: Context, *, message: str) -> None:
        """Add the external message for your embed."""
        self.embeds[ctx.author.id] = EmbedInfo(
            message, self.embeds[ctx.author.id].embed
        )
        await ctx.send("✅ Successfully set the message content for embed.")

    @embed.group(invoke_without_command=True)
    async def author(self, ctx: Context) -> None:
        """Commands for configuring the author and options on the embed."""
        await ctx.send_help(ctx.command)

    @author.command()
    async def name(self, ctx: Context, *, name: t.Union[str, discord.Member]) -> None:
        """Set the name for the author on the embed."""
        embed = self.embeds[ctx.author.id].embed

        if isinstance(name, discord.Member):
            name = name.name

        embed.set_author(
            name=name, url=embed.author.url, icon_url=embed.author.icon_url
        )

        await ctx.send("✅ Successfully set the embed author.")

    @author.command()
    async def icon(self, ctx: Context, icon: t.Union[str, discord.Member]) -> None:
        """Set the author's icon in the embed."""
        embed = self.embeds[ctx.author.id].embed

        if isinstance(icon, discord.Member):
            icon = icon.avatar_url_as(format="png")

        embed.set_author(name=embed.author.name,
                         url=embed.author.url, icon_url=icon)
        await ctx.send("✅ Successfully set author's icon.")

    @author.command()
    async def url(self, ctx: Context, url: str) -> None:
        """Set the author's URL in the embed."""
        embed = self.embeds[ctx.author.id].embed
        embed.set_author(
            name=embed.author.name, url=url, icon_url=embed.author.icon_url
        )
        await ctx.send("✅ Successfully set author's URL.")
