import base64
import difflib
import hashlib
import re
import textwrap
import typing as t
import unicodedata

from discord import Color, Embed
from discord.ext.commands import Cog, Context, command

from bot import Bot, config


class Conversion(Cog):
    """This is a Cog for converting and encoding strings."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.hash_algos = sorted(
            [h for h in hashlib.algorithms_available if h.islower()]
        )

    @command(name="ascii")
    async def _ascii(self, ctx: Context, *, text: str) -> None:
        """Convert a string to ascii."""
        ascii_text = " ".join(str(ord(letter)) for letter in text)
        description = textwrap.dedent(
            f"""
            • **Text:** `{text}`
            • **ASCII:** `{ascii_text}`
            """
        )
        embed = Embed(title="ASCII Convertor", description=description)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def unascii(self, ctx: Context, *, ascii_text: str) -> None:
        """Convert ascii to string."""
        try:
            text = "".join(chr(int(i)) for i in ascii_text.split(" "))
            description = textwrap.dedent(
                f"""
                • **ASCII:** `{ascii_text}`
                • **Text:** `{text}`
                """
            )
            embed = Embed(title="ASCII Convertor", description=description)
            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

            await ctx.send(embed=embed)
        except ValueError:
            await ctx.send(
                f"Invalid sequence. Example usage : `{config.COMMAND_PREFIX}unascii 104 101 121`"
            )

    @command()
    async def byteconvert(self, ctx: Context, value: int, unit: str = "Mio") -> None:
        """Convert into Bytes.

        Accepted units are: `O`, `Kio`, `Mio`, `Gio`, `Tio`, `Pio`, `Eio`, `Zio`, `Yio`
        """
        units = ("O", "Kio", "Mio", "Gio", "Tio", "Pio", "Eio", "Zio", "Yio")
        unit = unit.capitalize()

        if unit not in units:
            await ctx.send(f"Available units are `{'`, `'.join(units)}`.")
            return

        embed = Embed(title="Binary Convertor")
        index = units.index(unit)

        for i, u in enumerate(units):
            result = round(value / 2 ** ((i - index) * 10), 14)
            embed.add_field(name=u, value=result)

            embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command(name="hash")
    async def _hash(self, ctx: Context, algorithm: str, *, text: str) -> None:
        """Hash a string using specified algorithm."""
        algo = algorithm.lower()

        if algo not in self.hash_algos:
            close_matches = difflib.get_close_matches(
                algo, self.hash_algos, n=1)
            message = f"`{algo}` not available."
            if close_matches:
                message += f"\nDid you mean `{close_matches[0]}`?"
            await ctx.send(message)
            return

        try:
            hash_object = getattr(hashlib, algo)(text.encode("utf-8"))
        except AttributeError:
            hash_object = hashlib.new(algo, text.encode("utf-8"))

        description = textwrap.dedent(
            f"""
            • **Text:** `{text}`
            • **Hashed:** `{hash_object.hexdigest()}`
            """
        )

        embed = Embed(title=f"{algorithm} hash", description=description)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def encode(self, ctx: Context, *, text: str) -> None:
        """Convert a string to binary."""
        message_bytes = text.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")

        embed = Embed(title="Base64 Encode", description=base64_message)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def decode(self, ctx: Context, *, text: str) -> None:
        """Convert a binary to string."""
        base64_bytes = text.encode("ascii")
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode("ascii")

        embed = Embed(title="Base64 Decode", description=message)
        embed.set_footer(text=f"Invoked by {str(ctx.message.author)}")

        await ctx.send(embed=embed)

    @command()
    async def charinfo(self, ctx: Context, *, characters: str) -> None:
        """Shows you information on up to 25 unicode characters."""
        match = re.match(r"<(a?):(\w+):(\d+)>", characters)
        if match:
            embed = Embed(
                title="Non-Character Detected",
                description="Only unicode characters can be processed, but a custom Discord emoji was found. Please remove it and try again.",
            )
            embed.colour = Color.red()
            await ctx.send(embed=embed)
            return

        if len(characters) > 25:
            embed = Embed(title=f"Too many characters ({len(characters)}/25)")
            embed.colour = Color.red()
            await ctx.send(embed=embed)
            return

        def get_info(char: str) -> t.Tuple[str, str]:
            digit = f"{ord(char):x}"

            if len(digit) <= 4:
                u_code = f"\\u{digit:>04}"
            else:
                u_code = f"\\U{digit:>08}"

            url = f"https://www.compart.com/en/unicode/U+{digit:>04}"
            name = f"[{unicodedata.name(char, '')}]({url})"
            info = f"`{u_code.ljust(10)}`: {name} - {char}"
            return info, u_code

        charlist, rawlist = zip(*(get_info(c) for c in characters))

        embed = Embed(description="\n".join(charlist))
        embed.set_author(name="Character Info")

        if len(characters) > 1:
            embed.add_field(
                name="Raw", value=f"`{''.join(rawlist)}`", inline=False)

        await ctx.send(embed=embed)
