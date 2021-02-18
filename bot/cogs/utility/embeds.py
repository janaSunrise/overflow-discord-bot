from collections import defaultdict, namedtuple

import discord
from discord.ext.commands import (
    Cog,
    Context,
    ColorConverter,
    group,
)

from bot import Bot

EmbedInfo = namedtuple('EmbedInfo', ['message', 'embed'])


class Embeds(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.embeds = defaultdict(lambda: EmbedInfo("", discord.Embed()))

    @group(invoke_without_command=True)
    async def embed(self, ctx: Context) -> None:
        await ctx.send_help(ctx.command)

    @embed.command()
    async def show(self, ctx: Context) -> None:
        """Show your embed, how it looks before using it."""
        await ctx.send(self.embeds[ctx.author.id].message, embed=self.embeds[ctx.author.id].embed)

    @embed.command()
    async def reset(self, ctx: Context) -> None:
        """Reset your created embed."""
        self.embeds[ctx.author.id] = EmbedInfo("", discord.Embed())
        await ctx.send("Your embed was successfully reset.")

    @embed.command()
    async def title(self, ctx: Context, *, title: str) -> None:
        """Set the title field for your embed."""
        self.embeds[ctx.author.id].embed.title = title
        await ctx.send(f"Set title to `{title}`.")

    @embed.command(name="description")
    async def description_(self, ctx: Context, *, description: str) -> None:
        """Set description for your embed."""
        self.embeds[ctx.author.id].embed.description = description
        await ctx.send("Set the description successfully.")

    @embed.command()
    async def color(self, ctx: Context, color: ColorConverter) -> None:
        """Add colors to make your embed better!"""
        self.embeds[ctx.author.id].embed.color = color
        await ctx.send(f"Set color to `{color}`")

    @embed.command()
    async def footer(self, ctx: Context, *, footer_text: str) -> None:
        """Set the footer message for your embed."""
        self.embeds[ctx.author.id].embed.set_footer(text=footer_text)
        await ctx.send("Successfully set the footer.")

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
                await ctx.send("Invalid image extension to parse.")
                return
            else:
                self.embeds[ctx.author.id].embed.set_image(url=attachment.url)
        else:
            await ctx.send("Please supply an URL or upload an image to add to the embed.")
            return

        await ctx.send("Successfully set the image.")

    @embed.command()
    async def message(self, ctx: Context, *, message: str) -> None:
        """Add the external message for your embed."""
        self.embeds[ctx.author.id] = EmbedInfo(message, self.embeds[ctx.author.id].embed)
        await ctx.send("Successfully set the message content for embed.")
