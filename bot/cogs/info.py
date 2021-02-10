import codecs
import inspect
import os
import pathlib
import textwrap

import discord
from discord.ext import commands
from discord.ext import menus

from bot import Bot
from bot.utils.pages import CodeInfoSource, SauceSource

ZWS = "\u200b"


class Info(commands.Cog):
    """Get info about the bot."""
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(ignore_extra=True)
    async def code(self, ctx: commands.Context) -> None:
        """Return stats about the bot's code."""
        total = 0
        file_amount = 0
        list_of_files = []

        for filepath, _, files in os.walk('bot'):
            for name in files:
                if name.endswith('.py'):
                    file_lines = 0
                    file_amount += 1
                    with codecs.open('./' + str(pathlib.PurePath(filepath, name)), 'r', 'utf-8') as file:
                        for _, line in enumerate(file):
                            if line.strip().startswith('#') or len(
                                    line.strip()) == 0:
                                pass
                            else:
                                total += 1
                                file_lines += 1

                    final_path = filepath + os.path.sep + name
                    list_of_files.append(final_path.split('.' + os.path.sep)[-1] + f" : {file_lines} lines")

        paginator = commands.Paginator(
            max_size=2048,
        )

        for line in list_of_files:
            paginator.add_line(line)

        pages = menus.MenuPages(
            source=CodeInfoSource(
                f"{self.bot.user.name}'s structure",
                f"I am made of {total} lines of Python, spread across {file_amount} files !",
                paginator.pages,
                per_page=1,
            ),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

        # embed = discord.Embed(colour=discord.Colour.blurple())
        # embed.add_field(
        #     name=f"{self.bot.user.name}'s structure",
        #     value="\n".join(sorted(list_of_files)),
        # )
        # embed.set_footer(
        #     text=(
        #         f"I am made of {total} lines of Python, spread across "
        #         f"{file_amount} files !"
        #     ),
        # )
        # await ctx.send(embed=embed)

    @commands.command(aliases=["sauce"])
    async def source(self, ctx: commands.Context, *, command_name: str) -> None:
        """Get the source code of a command."""
        command = self.bot.get_command(command_name)

        if not command:
            await ctx.send(f"No command named `{command_name}` found.")
            return

        try:
            source_lines, _ = inspect.getsourcelines(command.callback)
        except (TypeError, OSError):
            await ctx.send(
                f"I was unable to retrieve the source for `{command_name}` for some reason."
            )
            return

        source_lines = textwrap.dedent("".join(source_lines).replace("```", f"`{ZWS}`{ZWS}`")).split("\n")
        paginator = commands.Paginator(
            prefix="```py",
            suffix="```",
            max_size=2048,
        )

        for line in source_lines:
            paginator.add_line(line)

        pages = menus.MenuPages(
            source=SauceSource(
                paginator.pages,
                per_page=1,
            ),
            clear_reactions_after=True,
        )
        await pages.start(ctx)


def setup(bot: Bot) -> None:
    bot.add_cog(Info(bot))
