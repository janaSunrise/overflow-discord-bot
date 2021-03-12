import collections
import enum
import io
import os
import platform
import textwrap
import time
import traceback
import typing as t
from contextlib import redirect_stdout
from datetime import datetime

import humanize
import psutil
import texttable
from discord import (Activity, ActivityType, Color, DiscordException, Embed,
                     Game, Status)
from discord import __version__ as discord_version
from discord.ext.commands import Cog, Context, group, is_owner
from jishaku.cog import OPTIONAL_FEATURES, STANDARD_FEATURES

from bot import Bot, config
from bot.databases.command_stats import CommandStats


class CounterKeys(enum.Enum):
    MESSAGES_RECIEVED = 0x100

    def __repr__(self) -> str:
        return self.name


class Sudo(*STANDARD_FEATURES, *OPTIONAL_FEATURES, Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot=bot)
        self.bot = bot
        self._last_eval_result = None
        self.sessions = set()

    def get_uptime(self) -> str:
        """Get formatted server uptime."""
        now = datetime.utcnow()
        delta = now - self.bot.start_time

        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)

        if days:
            formatted = f"{days} days, {hours} hr, {minutes} mins, and {seconds} secs"
        else:
            formatted = f"{hours} hr, {minutes} mins, and {seconds} secs"
        return formatted

    @Cog.listener()
    async def on_socket_response(self, msg: t.Any) -> None:
        """Cog listener for socket responses."""
        self.bot.socket_stats[msg.get("t")] += 1

    @group(hidden=True)
    @is_owner()
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""

    @sudo.command()
    async def shutdown(self, ctx: Context) -> None:
        """Turn the bot off."""
        await ctx.message.add_reaction("✅")
        await self.bot.close()

    @sudo.command()
    async def restart(self, ctx: Context) -> None:
        """Restart the bot."""
        await ctx.message.add_reaction("✅")
        await self.bot.close()

        time.sleep(1)
        os.system("python -m pipenv run start")

    async def _manage_cog(
        self, ctx: Context, process: str, extension: t.Optional[str] = None
    ) -> None:
        from bot.core.loader import COGS

        if not extension:
            extensions = COGS
        else:
            extensions = [f"bot.cogs.{extension}"]

        for ext in extensions:
            try:
                if process == "load":
                    self.bot.load_extension(ext)
                elif process == "unload":
                    self.bot.unload_extension(ext)
                elif process == "reload":
                    self.bot.unload_extension(ext)
                    self.bot.load_extension(ext)
                else:
                    await ctx.send("❌ Invalid process for extensions")
            except DiscordException:
                await ctx.send(
                    embed=Embed(
                        title="Exception",
                        description=f"```py\n{traceback.format_exc()}\n```",
                        color=Color.blue(),
                    )
                )
            else:
                await ctx.send("✅")

    @sudo.command()
    async def load(self, ctx: Context, extension: t.Optional[str]) -> None:
        """Load a cog."""
        await self._manage_cog(ctx, "load", extension)

    @sudo.command()
    async def unload(self, ctx: Context, extension: t.Optional[str]) -> None:
        """Unload a cog."""
        await self._manage_cog(ctx, "unload", extension)

    @sudo.command()
    async def reload(self, ctx: Context, extension: t.Optional[str]) -> None:
        """Unload and then load a cog."""
        await self._manage_cog(ctx, "reload", extension)

    @sudo.command(aliases=["status"])
    async def botstatus(self, ctx: Context, status: str, *, status_info: str) -> None:
        """Change the status of the bot.
        `botstatus playing <new status>` - Change playing status
        `botstatus watching <new status>` - Change watching status
        `botstatus listening <new status>` - Change listening status
        """
        statuses = ["playing", "watching", "listening"]
        if status.lower() not in statuses:
            await ctx.send("Invalid status type!")
            return

        if status.lower() == "playing":
            try:
                await self.bot.change_presence(
                    activity=Game(type=0, name=status_info), status=Status.online
                )
                await ctx.send(
                    f"Successfully changed playing status to **{status_info}**"
                )
            except DiscordException:
                await ctx.send(
                    embed=Embed(
                        title="Exception",
                        description=f"```py\n{traceback.format_exc()}\n```",
                        color=Color.blue(),
                    )
                )

        elif status.lower() == "watching":
            try:
                await self.bot.change_presence(
                    activity=Activity(
                        type=ActivityType.watching, name=status_info)
                )
                await ctx.send(
                    f"Successfully changed watching status to **{status_info}**"
                )
            except DiscordException:
                await ctx.send(
                    embed=Embed(
                        title="Exception",
                        description=f"```py\n{traceback.format_exc()}\n```",
                        color=Color.blue(),
                    )
                )

        elif status.lower() == "listening":
            try:
                await self.bot.change_presence(
                    activity=Activity(
                        type=ActivityType.listening, name=status_info)
                )
                await ctx.send(
                    f"Successfully changed listening status to **{status_info}**"
                )
            except DiscordException:
                await ctx.send(
                    embed=Embed(
                        title="Exception",
                        description=f"```py\n{traceback.format_exc()}\n```",
                        color=Color.blue(),
                    )
                )

    @sudo.command()
    async def socketstats(self, ctx: Context) -> None:
        """Get the bot's socket stats."""
        delta = datetime.utcnow() - self.bot.start_time
        minutes = delta.total_seconds() / 60

        total = sum(self.bot.socket_stats.values())
        cpm = total / minutes
        await ctx.send(
            embed=Embed(
                title="Socket stats",
                description=f"{total} socket events observed ({cpm:.2f}/minute):\n`{self.bot.socket_stats}`",
                color=Color.blue(),
            )
        )

    @sudo.command()
    async def stats(self, ctx: Context) -> None:
        """Show full bot stats."""
        general = textwrap.dedent(
            f"""
            • Servers: **`{len(self.bot.guilds)}`**
            • Members: **`{len(set(self.bot.get_all_members()))}`**
            • Commands: **`{len(self.bot.commands)}`**
            • Uptime: **`{self.get_uptime()}`**
            """
        )
        system = textwrap.dedent(
            f"""
            • Python: **`{platform.python_version()} with {platform.python_implementation()}`**
            • discord.py: **`{discord_version}`**
            """
        )
        shard_info = textwrap.dedent(
            f"""
            • Shard count: **`{self.bot.shard_count}`**
            """
        )
        if ctx.guild:
            shard_info += f"• Current shard: **`{ctx.guild.shard_id}`**"

        embed = Embed(title="BOT STATISTICS", color=Color.blue())
        embed.add_field(name="**❯ General**", value=general, inline=False)
        embed.add_field(name="**❯ System**", value=system, inline=False)
        embed.add_field(name="**❯ Shard info**",
                        value=shard_info, inline=False)

        process = psutil.Process()
        with process.oneshot():
            memory_usage = process.memory_full_info().uss / 1024 ** 2
            cpu_usage = psutil.cpu_percent()

            mem = process.memory_full_info()
            name = process.name()
            pid = process.pid
            threads = process.num_threads()
            value = textwrap.dedent(
                f"""
                • CPU usage: **`{cpu_usage:.2f}%`**
                • Memory usage: **`{memory_usage:.2f} MB`**

                • Physical memory: **`{humanize.naturalsize(mem.rss)}`**
                • Virtual memory: **`{humanize.naturalsize(mem.vms)}`**

                • PID: `{pid}` (`{name}`)
                • Threads: **`{threads}`**
                • Core count: **`{psutil.cpu_count(logical=False)}`** / **`{psutil.cpu_count(logical=True)}`**
                """
            )
            embed.add_field(
                name="**❯ Memory info**",
                value=value,
                inline=False,
            )

        uname = platform.uname()
        system = textwrap.dedent(
            f"""
            • System: **`{uname.system}`**
            • Node Name: **`{uname.node}`**
            
            • Release: **`{uname.release}`**
            • Version: **`{uname.version}`**
            
            • Machine: **`{uname.machine}`**
            • Processor: **`{uname.processor}`**            
            """
        )
        embed.add_field(
            name="**❯ System info**",
            value=system,
            inline=False,
        )

        embed.set_author(
            name=f"{self.bot.user.name}'s Stats", icon_url=self.bot.user.avatar_url
        )
        embed.set_footer(text=f"Made by {config.creator}.")

        await ctx.send(embed=embed)

    @sudo.command()
    async def shards(self, ctx: Context) -> None:
        """Get the shard info about the bot."""
        shard_info = ""

        for key, item in self.bot.shards.items():
            shard_info += (
                f"**`[{key}]`**:\n"
                f"Latency: **`{round(item.latency * 1000)}ms`**\n"
                f"Shard count: `{item.shard_count}`\n"
            )

        await ctx.send(
            embed=Embed(
                title="Cluster info",
                description=textwrap.dedent(
                    f"""
                Clusters IDs: `{self.bot.shard_ids}`

                """
                    + shard_info
                ),
                color=Color.blue(),
            )
        )

    @sudo.command(aliases=["shard-stats"])
    async def shard_stats(self, ctx: Context) -> None:
        """Provides statistics for each shard of the bot."""
        output = []
        latencies = dict(ctx.bot.latencies)

        columns = (
            "Shard",
            "Guilds",
            "Total Members",
            "Loaded Members",
            "Music",
            "Messages",
            "Latency",
        )
        shard_stats = {
            shard_id: self.get_shard_stats(ctx, shard_id)
            for shard_id in latencies.keys()
        }

        table = texttable.Texttable()
        table.set_deco(texttable.Texttable.HEADER | texttable.Texttable.VLINES)
        table.set_cols_align(["r"] * len(columns))
        table.set_cols_valign(["t"] + ["i"] * (len(columns) - 1))
        table.header(columns)
        for shard_id, stats in sorted(shard_stats.items()):
            stats["Latency"] = latencies.get(shard_id) or "N/A"
            table.add_row([shard_id] + [stats[key] for key in columns[1:]])

        output.append(table.draw())
        output.append("")
        output.append(f"discord.py: {discord_version}")

        output = "\n".join(output)
        await ctx.send(f"```{output}```")

    @staticmethod
    def get_shard_stats(ctx, shard_id):
        counters = collections.Counter()
        counters["Shard"] = shard_id

        for guild in ctx.bot.guilds:
            if guild.shard_id != shard_id:
                continue
            guild_counts = ctx.bot.guild_counters[guild.id]
            counters["Guilds"] += 1
            counters["Total Members"] += guild.member_count
            counters["Loaded Members"] += len(guild.members)
            counters["Messages"] += guild_counts[CounterKeys.MESSAGES_RECIEVED]

            if any(guild.me.id in vc.voice_states for vc in guild.voice_channels):
                counters["Music"] += 1

        return counters

    @staticmethod
    def cleanup_code(content: str) -> str:
        """Automatically removes code blocks from the code."""
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        return content.strip("` \n")

    @sudo.command(name="eval")
    async def _eval(self, ctx: Context, *, code: str):
        """Eval some code"""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "guild": ctx.guild,
            "channel": ctx.channel,
            "author": ctx.author,
            "message": ctx.message,
            "_": self._last_eval_result,
        }
        env.update(globals())

        code = self.cleanup_code(code)
        buffer = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(code, " ")}'

        try:
            exec(to_compile, env)
        except Exception as error:
            return await ctx.send(f"```py\n{error.__class__.__name__}: {error}\n``")

        func = env["func"]

        try:
            with redirect_stdout(buffer):
                ret = await func()
        except Exception:
            value = buffer.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = buffer.getvalue()
            try:
                await ctx.message.add_reaction("\N{INCOMING ENVELOPE}")
            except DiscordException:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
                else:
                    self._last_eval_result = ret
                    await ctx.send(f"```py\n{value}{ret}\n```")

    @sudo.command(aliases=["command-stats", "cmd-stats"])
    async def command_stats(self, ctx: Context) -> None:
        rows = await CommandStats.get_stats(self.bot.database)

        embed = Embed(
            title="Usage stats",
            colour=Color.blue(),
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=str(ctx.author.avatar_url),
        )
        records = sorted(
            rows,
            key=lambda elem: elem["usage_count"],
            reverse=True,
        )[:10]

        for record in records:
            embed.add_field(
                name=f"• {record['command']}",
                value=f"Usage count: {record['usage_count']}",
                inline=False,
            )
        await ctx.send(embed=embed)

    @Cog.listener("on_command_completion")
    async def stats_listener(self, ctx: Context) -> None:
        """Log usage of the bot."""
        if await ctx.bot.is_owner(ctx.author):
            return

        record = await CommandStats.get_command_stats(
            self.bot.database, ctx.command.name
        )

        if record:
            await CommandStats.set_command_stats(
                self.bot.database, ctx.command.name, record["usage_count"] + 1
            )
        else:
            await CommandStats.set_command_stats(self.bot.database, ctx.command.name, 1)
