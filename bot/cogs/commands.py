import asyncio
import json
import re
import textwrap
import time
import typing as t
from datetime import datetime

import discord
from dateutil.relativedelta import relativedelta
from discord.ext.commands import (BadArgument, BucketType, Cog, Context,
                                  command, cooldown, group, has_permissions)

from bot import Bot, config
from bot.core.converters import TimeConverter
from bot.databases.prefix import Prefix
from bot.utils.time import humanize_time


class Commands(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @group(invoke_without_command=True)
    @has_permissions(manage_channels=True)
    async def prefix(self, ctx: Context) -> None:
        """Set custom prefix for the bot."""
        await ctx.send_help(ctx.command)

    @prefix.command()
    async def set(self, ctx: Context, prefix: t.Optional[str] = None) -> None:
        """Set the custom prefix for the current guild / DM."""
        if prefix is not None:
            if prefix.startswith(f"{self.bot.default_prefix}help"):
                await ctx.send(f"You can't use {prefix} as a prefix.")
                return

            ctx_id = self.bot.get_id(ctx)

            await Prefix.set_prefix(self.bot.database, ctx_id, prefix=prefix)
            self.bot.prefix_dict[ctx_id] = [prefix, self.bot.default_prefix]

            await ctx.send(
                f"Prefix changed to **`{discord.utils.escape_markdown(prefix)}`**"
            )
            return

        old_prefix = discord.utils.escape_markdown(
            await self.bot.get_msg_prefix(ctx.message, False)
        )
        await ctx.send(f"The prefix for this channel is **`{old_prefix}`**")

    @prefix.command()
    async def reset(self, ctx: Context) -> None:
        """Reset the prefix for the current guild / DM."""
        prefix = config.COMMAND_PREFIX
        ctx_id = self.bot.get_id(ctx)

        await Prefix.set_prefix(self.bot.database, ctx_id, prefix=prefix)
        self.bot.prefix_dict[ctx_id] = prefix

        await ctx.send(
            f"Prefix changed back to **`{discord.utils.escape_markdown(prefix)}`**"
        )
        return

    @command()
    async def ping(self, ctx: Context) -> None:
        """Show bot ping."""
        start = time.perf_counter()

        embed = discord.Embed(
            title="Info", description="Pong!", color=discord.Color.blurple()
        )
        message = await ctx.send(embed=embed)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        discord_start = time.monotonic()
        async with self.bot.session.get("https://discord.com/") as resp:
            if resp.status == 200:
                discord_end = time.monotonic()
                discord_ms = f"{round((discord_end - discord_start) * 1000)}ms"
            else:
                discord_ms = "fucking dead"

        desc = textwrap.dedent(
            f"""
            :ping_pong: Pong!
            Bot Ping: **{round(self.bot.latency * 1000)}ms**
            Message ping: **{duration}ms**
            Discord Server Ping: **{discord_ms}**
            """
        )

        embed = discord.Embed(
            title="Info", description=desc, color=discord.Color.blurple()
        )
        await message.edit(embed=embed)

    @command()
    async def paste(self, ctx: Context, *, text: str = None) -> None:
        """Creates a Paste out of the text specified."""
        payload = {
            "name": "Overflow paste",
            "description": "Paste generation using paste command",
        }

        if text is not None:
            payload["files"] = [
                {"name": "file.txt", "content": {"format": "text", "value": text}}
            ]
        elif ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            content = (await attachment.read()).decode("utf-8")
            payload["files"] = [
                {
                    "name": attachment.filename,
                    "content": {"format": "text", "value": content},
                }
            ]
        else:
            await ctx.send(":x: Please specify text or upload an file.")
            return

        async with self.bot.session.post(
            "https://api.paste.gg/v1/pastes",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        ) as resp:
            key = (await resp.json())["result"]["id"]
            file_paste = "https://paste.gg/" + key

            await ctx.send(
                embed=discord.Embed(
                    title="File paste",
                    description=file_paste,
                    color=discord.Color.blue(),
                )
            )

    @staticmethod
    def _clean_code(code: str) -> str:
        codeblock_match = re.fullmatch(r"```(.*\n)?((?:[^`]*\n*)+)```", code)
        if codeblock_match:
            lang = codeblock_match.group(1)
            code = codeblock_match.group(2)
            ret = lang if not code else code
            if ret[-1] == "\n":
                ret = ret[:-1]
            return ret

        simple_match = re.fullmatch(r"`(.*\n*)`", code)
        if simple_match:
            return simple_match.group(1)

        return code

    @cooldown(1, 10, BucketType.member)
    async def shorten(self, ctx: Context, *, link: str) -> None:
        """Make a link shorter using the tinyurl api."""
        if not link.startswith("https://"):
            await ctx.send(f"Invalid link: `{link}`. Enter a valid URL.")
            return

        url = link.strip("<>")
        url = f"http://tinyurl.com/api-create.php?url={url}"

        async with self.bot.session.get(url) as resp:
            if resp.status != 200:
                await ctx.send(
                    "Error retrieving shortened URL, please try again in a minute."
                )
                return
            shortened_link = await resp.text()

        embed = discord.Embed(color=discord.Color.blurple())
        embed.add_field(name="Original Link", value=link, inline=False)
        embed.add_field(name="Shortened Link",
                        value=shortened_link, inline=False)
        await ctx.send(embed=embed)

    @command(aliases=("poll",))
    async def vote(self, ctx: Context, title: str, *options: str) -> None:
        """
        Build a quick voting poll with matching reactions with the provided options.
        A maximum of 20 options can be provided, as Discord supports a max of 20
        reactions on a single message.

        Syntax: [p]vote "Option 1" "Option 2" ... "Option n"
        """
        codepoint_start = 127462

        if len(options) < 2:
            raise BadArgument("Please provide at least 2 options.")

        if len(options) > 20:
            raise BadArgument("I can only handle 20 options!")

        options = {
            chr(i): f"{chr(i)} - {v}"
            for i, v in enumerate(options, start=codepoint_start)
        }

        embed = discord.Embed(
            title=title,
            description="\n".join(options.values()),
            color=discord.Color.blurple(),
        )
        message = await ctx.send(embed=embed)

        for reaction in options:
            await message.add_reaction(reaction)

    @command()
    @cooldown(1, 10, BucketType.member)
    async def countdown(
        self,
        ctx: Context,
        duration: TimeConverter,
        *,
        description: t.Optional[str] = "Countdown!",
    ) -> None:
        """A countdown timer that counts down for the specific duration."""
        embed = discord.Embed(
            title="Timer", description=description, color=discord.Color.blurple()
        )
        embed.add_field(name="**Countdown**", value=humanize_time(duration))
        message = await ctx.send(embed=embed)

        final_time = datetime.utcnow() + duration
        while True:
            if final_time <= datetime.utcnow():
                break
            duration = relativedelta(final_time, datetime.utcnow())

            embed.set_field_at(0, name="**Countdown**",
                               value=humanize_time(duration))
            await message.edit(embed=embed)

            await asyncio.sleep(1)

        embed.set_field_at(0, name="**Countdown**", value="Time's Up!")
        await message.edit(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
