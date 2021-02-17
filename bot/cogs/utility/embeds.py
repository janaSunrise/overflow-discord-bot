from collections import defaultdict, namedtuple

import discord
from discord.ext import commands

from bot import Bot

EmbedInfo = namedtuple('EmbedInfo', ['info', 'embed'])


class Embeds(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.embeds = defaultdict(lambda: EmbedInfo("", discord.Embed()))

    @commands.group(invoke_without_command=True)
    async def embed(self, ctx: commands.Context) -> None:
        await ctx.send_help(ctx.command)

    @embed.command()
    async def show(self, ctx: commands.Context) -> None:
        await ctx.send(embed=self.embeds[ctx.author.id].embed)

    @embed.command()
    async def title(self, ctx: commands.Context, *, title: str) -> None:
        self.embeds[ctx.author.id].embed.title = title
        await ctx.send(f"Set title to `{title}`.")

    @embed.command(name="description")
    async def description_(self, ctx: commands.Context, *, description: str) -> None:
        self.embeds[ctx.author.id].embed.description = description
        await ctx.send("Set the description successfully.")

    @embed.command()
    async def color(self, ctx: commands.Context, color: commands.ColorConverter) -> None:
        self.embeds[ctx.author.id].embed.color = color
        await ctx.send(f"Set color to `{color}`")

    @embed.command()
    async def footer(self, ctx: commands.Context, *, footer_text: str) -> None:
        self.embeds[ctx.author.id].embed.color = footer_text
        await ctx.send("Successfully set the footer.")

    @embed.command()
    async def image(self, ctx: commands.Context, image_url: str = None) -> None:
        clean_image_extension = ["jpg", "jpeg", "png", "bmp"]
        attachment = ctx.message.attachments[0]

        if image_url is not None:
            self.embeds[ctx.author].embed.set_image(url=image_url)
        elif ctx.message.attachments:
            extension = attachment.filename.lower().split(".")
            if extension not in clean_image_extension:
                await ctx.send("Invalid image extension to parse.")
                return
            else:
                self.embeds[ctx.author].embed.set_image(url=attachment.url)
        else:
            await ctx.send("Please supply an URL or upload an image to add to the embed.")
            return

        await ctx.send("Successfully set the image.")

    @embed.command()
    async def message(self, ctx: commands.Context, *, message: str) -> None:
        self.embeds[ctx.author.id] = EmbedInfo(message, self.embeds[ctx.author.id].embed)
        await ctx.send("Successfully set the message content for embed.")
