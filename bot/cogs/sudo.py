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
from discord import Color, DiscordException, Embed
from discord import __version__ as discord_version
from discord.ext.commands import Cog, Context, group, is_owner
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES

from bot import Bot, config


class Sudo(*STANDARD_FEATURES, *OPTIONAL_FEATURES, Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot=bot)
        self._last_eval_result = None

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

    @group(hidden=True)
    @is_owner()
    async def sudo(self, ctx: Context) -> None:
        """Administrative information."""
        pass

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

    async def _manage_cog(self, ctx: Context, process: str, extension: t.Optional[str] = None) -> None:
        if not extension:
            extensions = self.bot.extension_list
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
                    await ctx.send("Invalid process for extensions")
            except DiscordException:
                await ctx.send(f"```py\n{traceback.format_exc()}\n```")
            else:
                await ctx.send("\N{SQUARED OK}")

    @sudo.command()
    async def load(self, ctx: Context, extension: t.Optional[str]) -> None:
        await self._manage_cog(ctx, "load", extension)

    @sudo.command()
    async def unload(self, ctx: Context, extension: t.Optional[str]) -> None:
        await self._manage_cog(ctx, "unload", extension)

    @sudo.command()
    async def reload(self, ctx: Context, extension: t.Optional[str]) -> None:
        await self._manage_cog(ctx, "reload", extension)

    @sudo.command()
    async def stats(self, ctx: Context) -> None:
        """Show full bot stats."""
        general = textwrap.dedent(
            f"""
            • Servers: **`{len(self.bot.guilds)}`**
            • Commands: **`{len(self.bot.commands)}`**
            • Members: **`{len(set(self.bot.get_all_members()))}`**
            • Uptime: **`{self.get_uptime()}`**
            """
        )
        system = textwrap.dedent(
            f"""
            • Python: **`{platform.python_version()} with {platform.python_implementation()}`**
            • discord.py: **`{discord_version}`**
            """
        )

        embed = Embed(title="BOT STATISTICS", color=Color.blue())
        embed.add_field(name="**❯ General**", value=general, inline=True)
        embed.add_field(name="**❯ System**", value=system, inline=True)

        process = psutil.Process()
        with process.oneshot():
            mem = process.memory_full_info()
            name = process.name()
            pid = process.pid
            threads = process.num_threads()
            value = textwrap.dedent(
                f"""
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

        embed.set_author(name=f"{self.bot.user.name}'s Stats", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f"Made by {config.creator}.")

        await ctx.send(embed=embed)

    @staticmethod
    def cleanup_code(content: str) -> str:
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    @sudo.command(name='eval')
    async def _eval(self, ctx: Context, *, code: str):
        """Eval some code"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            'message': ctx.message,
            '_': self._last_eval_result
        }
        env.update(globals())

        code = self.cleanup_code(code)
        buffer = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(code, " ")}'

        try:
            exec(to_compile, env)
        except Exception as error:
            return await ctx.send(f'```py\n{error.__class__.__name__}: {error}\n``')

        func = env['func']

        try:
            with redirect_stdout(buffer):
                ret = await func()
        except Exception:
            value = buffer.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = buffer.getvalue()
            try:
                await ctx.message.add_reaction('\N{INCOMING ENVELOPE}')
            except DiscordException:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
                    await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot: Bot) -> None:
    bot.add_cog(Sudo(bot))
