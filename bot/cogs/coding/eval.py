import json
import re
from pathlib import Path
from typing import Optional

from discord import Embed, Message
from discord.ext import commands, menus, tasks
from discord.ext.commands import Cog, Context, command
from discord.utils import escape_mentions
from yaml import safe_load

from bot import Bot
from bot.utils.eval_helper import EvalHelper, FormatOutput, Tio
from bot.utils.pages import CodeInfoSource

SOFT_RED = 0xCD6D6D
GREEN = 0x1F8B4C


class Eval(Cog):
    """Safe evaluation of Code using Tio Run Api."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.languages = None
        self.languages_url = "https://tio.run/languages.json"
        self.update_languages.start()

        with Path("bot/assets/default_langs.yml").open(encoding="utf8") as file:
            self.default_languages = safe_load(file)

        with Path("bot/assets/wrapping.yml").open(encoding="utf8") as file:
            self.wrapping = safe_load(file)

        with Path("bot/assets/quick_map.yml").open(encoding="utf8") as file:
            self.quick_map = safe_load(file)

    @tasks.loop(hours=5)
    async def update_languages(self) -> None:
        """Update list of languages supported by api every 5 hour."""
        async with self.bot.session.get(self.languages_url) as response:
            languages = tuple(sorted(json.loads(await response.text())))
            self.languages = languages

    @command(aliases=["language-list", "langs", "langs-list"])
    async def language_supported(self, ctx: Context) -> None:
        """Show all the languages supported by this compiler."""
        paginator = commands.Paginator(
            max_size=2048,
        )

        for line in self.languages:
            paginator.add_line(line)

        pages = menus.MenuPages(
            source=CodeInfoSource(
                "Languages supported by the compiler",
                None,
                paginator.pages,
                per_page=1,
            ),
            clear_reactions_after=True,
        )
        await pages.start(ctx)

    @command(name="eval")
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def eval_command(
        self, ctx: Context, language: str, *, code: str = ""
    ) -> Optional[Message]:
        """
        eval <language> [--wrapped] [--stats] <code>

        for command-line-options, compiler-flags and arguments you may add a line starting with this argument, and
        after a space add your options, flags or args.

        stats  - option displays more information on execution consumption
        wrapped  - allows you to not put main function in some languages

        <code> may be normal code, but also an attached file, or a link from [hastebin](https://hastebin.com) or
        [Github gist](https://gist.github.com). If you use a link, your command must end with this syntax:
        `link=<link>` (no space around `=`) for instance : `!eval python link=https://hastebin.com/code.py`

        If the output exceeds 40 lines or Discord max message length, it will be put in a new hastebin and the link
        will be returned.
        """
        async with ctx.typing():
            eval_helper = EvalHelper(language)

            parsed_data = await eval_helper.parse(code)
            (
                inputs,
                code,
                lang,
                options,
                compiler_flags,
                command_line_options,
                args,
            ) = parsed_data
            text = None

            if ctx.message.attachments:
                text = await eval_helper.code_from_attachments(ctx)
                if not text:
                    return

            elif code.split(" ")[-1].startswith("link="):
                text = await eval_helper.code_from_url(ctx, code)
                if not text:
                    return

            elif code.strip("`"):
                text = code.strip("`")
                first_line = text.splitlines()[0]
                if re.fullmatch(r"( |[0-9A-z]*)\b", first_line):
                    text = text[len(first_line) + 1:]

            if text is None:
                raise commands.MissingRequiredArgument(
                    ctx.command.clean_params["code"])

            if lang in self.quick_map:
                lang = self.quick_map[lang]

            if lang in self.default_languages:
                lang = self.default_languages[lang]

            if lang not in self.languages:
                if not escape_mentions(lang):
                    embed = Embed(
                        title="MissingRequiredArgument",
                        description=f"Missing Argument Language.\n\nUsage:\n"
                        f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```",
                        color=SOFT_RED,
                    )
                else:
                    embed = Embed(
                        title="Language Not Supported",
                        description=f"Your language was invalid: {lang}\n"
                        f"All Supported languages: [here](https://tio.run)\n\nUsage:\n"
                        f"```{ctx.prefix}{ctx.command} {ctx.command.signature}```",
                        color=SOFT_RED,
                    )
                await ctx.send(embed=embed)
                return

            if options["--wrapped"]:
                if not (
                    any(map(lambda x: lang.split("-")[0] == x, self.wrapping))
                ) or lang in ("cs-mono-shell", "cs-csi"):
                    await ctx.send(f"`{lang}` cannot be wrapped")
                    return

                for beginning in self.wrapping:
                    if lang.split("-")[0] == beginning:
                        text = self.wrapping[beginning].replace("code", text)
                        break

            tio = Tio(lang, text, inputs, compiler_flags,
                      command_line_options, args)
            result = await tio.get_result()

            result = result.rstrip("\n")

            if not options["--stats"]:
                try:
                    start, end = (
                        result.rindex("Real time: "),
                        result.rindex("%\nExit code: "),
                    )
                    result = result[:start] + result[end + 2:]
                except ValueError:
                    pass

            format_output = FormatOutput(language=lang)

            if len(result) > format_output.max_output_length or result.count("\n") > format_output.max_lines:
                output = await eval_helper.paste(result)

                embed = format_output.format_hastebin_output(output, result)

                await ctx.send(content=f"{ctx.author.mention}", embed=embed)
                return

            embed = format_output.format_code_output(result)
            await ctx.send(content=f"{ctx.author.mention}", embed=embed)
