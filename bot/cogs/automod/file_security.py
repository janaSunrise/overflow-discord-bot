from contextlib import suppress
from os.path import splitext

import discord
from discord.ext.commands import Cog
from loguru import logger

from bot import Bot
from bot.utils.attachments import file_uploader

FILE_EMBED_DESCRIPTION = """
    Woops, your message got zapped by our spam filter.
    We currently don't allow binary / unknown attachments or any source files, so here are some tips you can use:

    • Try shortening your message, if it exceeds 2000 character limit
    to fit within the character limit or use a pasting service (see below)
    
    • To protect other users, we keep a watch on the binaries, and the executable files sent and more, in order
    to save them from malicious / harmful files.

    • If you're showing code, you can use codeblocks or use a pasting service like [mystb.in](https://mystb.in) or [paste.gg](https://paste.gg)
    """

WHITELIST_TYPES = (
    ".3gp",
    ".3g2",
    ".avi",
    ".bmp",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".wmv",
    ".gif",
    ".jpg",
    ".jpeg",
    ".png",
    ".svg",
    ".psd",
    ".ai",
    ".aep",
    ".mp3",
    ".wav",
    ".ogg",
)


class FileSecurity(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.attachments or not message.guild:
            return

        if message.author.permissions_in(message.channel).manage_messages:
            return

        attachments = []
        for attachment in message.attachments:
            extension = splitext(attachment.filename.lower())[1]

            if extension in WHITELIST_TYPES:
                continue
            attachments.append(attachment)

        if len(attachments) == 0:
            return

        logger.info(
            f"User <@{message.author.id}> posted a message on {message.guild.id} with protected "
            "attachments."
        )
        embed = discord.Embed(
            description=FILE_EMBED_DESCRIPTION, color=discord.Color.dark_blue()
        )

        with suppress(discord.NotFound, ConnectionError):
            await message.delete()
            await message.channel.send(f"Hey {message.author.mention}!", embed=embed)

            file_pastes = await file_uploader(attachments)

            if file_pastes is not None:
                paste_embed = discord.Embed(
                    color=discord.Color.gold(),
                    description=f"We uploaded the paste version of the files for you. The Paste(s) of the file(s) can "
                    f"be found at {file_pastes}",
                    title="Auto File Pastes!",
                )
                await message.channel.send(embed=paste_embed)
