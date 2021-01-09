import json
import re
from dataclasses import dataclass

from discord import Embed, Message, errors as discord_errors
from discord.ext import commands
from discord.utils import escape_mentions
from aiohttp import ContentTypeError

from bot import Bot
from bot.utils.codeswap import add_boilerplate
from bot.utils.errors import PistonInvalidContentType, PistonInvalidStatus, PistonNoOutput


@dataclass
class RunIO:
    input: Message
    output: Message


class Run(commands.Cog, name='CodeExecution'):
    def __init__(self, client: Bot) -> None:
        self.client = client
        self.languages = {
            'asm': 'nasm',
            'asm64': 'nasm64',
            'awk': 'awk',
            'bash': 'bash',
            'bf': 'brainfuck',
            'brainfuck': 'brainfuck',
            'c': 'c',
            'c#': 'csharp',
            'c++': 'cpp',
            'cpp': 'cpp',
            'cs': 'csharp',
            'csharp': 'csharp',
            'deno': 'deno',
            'denojs': 'deno',
            'denots': 'deno',
            'duby': 'ruby',
            'el': 'emacs',
            'elisp': 'emacs',
            'emacs': 'emacs',
            'elixir': 'elixir',
            'haskell': 'haskell',
            'hs': 'haskell',
            'go': 'go',
            'java': 'java',
            'javascript': 'javascript',
            'jelly': 'jelly',
            'jl': 'julia',
            'julia': 'julia',
            'js': 'javascript',
            'kotlin': 'kotlin',
            'lua': 'lua',
            'nasm': 'nasm',
            'nasm64': 'nasm64',
            'nim': 'nim',
            'node': 'javascript',
            'paradoc': 'paradoc',
            'perl': 'perl',
            'php': 'php',
            'php3': 'php',
            'php4': 'php',
            'php5': 'php',
            'py': 'python3',
            'py3': 'python3',
            'python': 'python3',
            'python2': 'python2',
            'python3': 'python3',
            'r': 'r',
            'rb': 'ruby',
            'ruby': 'ruby',
            'rs': 'rust',
            'rust': 'rust',
            'sage': 'python3',
            'swift': 'swift',
            'ts': 'typescript',
            'typescript': 'typescript',
        }
        self.run_IO_store = dict()  # Store the most recent /run message for each user.id
        self.run_regex = re.compile(
            r'(?s)/(?:edit_last_)?run(?: +(?P<language>\S*)\s*|\s*)(?:\n(?P<args>(?:[^\n\r\f\v]*\n)*?)\s*|\s*)```(?:(?P<syntax>\S+)\n\s*|\s*)(?P<source>.*)```'
        )

    async def get_run_output(self, ctx):
        if ctx.message.content.count('```') != 2:
            raise commands.BadArgument('Invalid command format (missing codeblock?)')

        match = self.run_regex.search(ctx.message.content)

        if not match:
            raise commands.BadArgument('Invalid command format')

        language, args, syntax, source = match.groups()

        if args:
            args = [arg for arg in args.strip().split('\n') if arg]

        if not language:
            language = syntax

        if language not in self.languages:
            raise commands.BadArgument(f'Unsupported language: {language}')

        if not source:
            raise commands.BadArgument(f'No source code found')

        # Add boilerplate code to supported languages
        source = add_boilerplate(language, source)

        # Call piston API
        language = self.languages[language]
        data = {'language': language, 'source': source, 'args': args}
        headers = {'Authorization': self.client.config["emkc_key"]}

        async with self.client.session.post(
            'https://emkc.org/api/v1/piston/execute',
            headers=headers,
            data=json.dumps(data)
        ) as response:
            try:
                r = await response.json()
            except ContentTypeError:
                raise PistonInvalidContentType()
        if not response.status == 200:
            raise PistonInvalidStatus(f'{response.status}')
        if r['output'] is None:
            raise PistonNoOutput()


        # Return early if no output was received
        if len(r['output']) == 0:
            return f'Your code ran without output {ctx.author.mention}'

        # Limit output to 30 lines maximum
        output = '\n'.join(r['output'].split('\n')[:30])

        # Prevent mentions in the code output
        output = escape_mentions(output)

        # Prevent code block escaping by adding zero width spaces to backticks
        output = output.replace("`", "`\u200b")

        truncate_indicator = '[...]'
        len_syntax = 0 if syntax is None else len(syntax)
        if len(output) > 1945-len_syntax+len(truncate_indicator):
            output = output[:1945-len_syntax] + truncate_indicator

        return (
            f'Here is your output {ctx.author.mention}\n'
            + f'```{syntax or ""}\n'
            + output
            + '```'
        )

    async def delete_last_output(self, user_id):
        try:
            msg_to_delete = self.run_IO_store[user_id].output
            del self.run_IO_store[user_id]
            await msg_to_delete.delete()
        except KeyError:
            # Message does not exist in store dicts
            return
        except discord_errors.NotFound:
            # Message no longer exists in discord (deleted by server admin)
            return

    @commands.command(aliases=['del'])
    async def delete(self, ctx):
        """
        Delete the most recent output message you caused
        Type "/run" or "/eval-help" for instructions
        """
        await self.delete_last_output(ctx.author.id)

    @commands.command()
    async def run(self, ctx, *, source=None):
        """
        Run some code
        Type "/run" or "/eval-help" for instructions
        """
        await ctx.trigger_typing()
        if not source:
            await self.send_howto(ctx)
            return
        try:
            run_output = await self.get_run_output(ctx)
            msg = await ctx.send(run_output)
        except commands.BadArgument as error:
            embed = Embed(
                title='Error',
                description=str(error),
                color=0x2ECC71
            )
            msg = await ctx.send(embed=embed)
        self.run_IO_store[ctx.author.id] = RunIO(input=ctx.message, output=msg)

    @commands.command(hidden=True)
    async def edit_last_run(self, ctx, *, source=None):
        """Run some edited code and edit previous message"""
        if not source:
            return
        try:
            msg_to_edit = self.run_IO_store[ctx.author.id].output
            run_output = await self.get_run_output(ctx)
            await msg_to_edit.edit(content=run_output, embed=None)
        except KeyError:
            return
        except discord_errors.NotFound:
            del self.run_IO_store[ctx.author.id]
            return
        except commands.BadArgument as error:
            # Edited message probably has bad formatting -> replace previous message with error
            embed = Embed(
                title='Error',
                description=str(error),
                color=0x2ECC71
            )
            try:
                await msg_to_edit.edit(content=None, embed=embed)
            except discord_errors.NotFound:
                # Message no longer exists in discord
                del self.run_IO_store[ctx.author.id]
            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if before.author.id not in self.run_IO_store:
            return
        if before.id != self.run_IO_store[before.author.id].input.id:
            return

        prefixes = await self.client.get_prefix(after)

        if isinstance(prefixes, str):
            prefixes = [prefixes, ]

        if any(after.content in (f'{prefix}delete', f'{prefix}del') for prefix in prefixes):
            await self.delete_last_output(after.author.id)
            return

        for prefix in prefixes:
            if after.content.lower().startswith(f'{prefix}run'):
                after.content = after.content.replace(f'{prefix}run', f'{prefix}edit_last_run')
                await self.client.process_commands(after)
                break

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if message.author.id not in self.run_IO_store:
            return
        if message.id != self.run_IO_store[message.author.id].input.id:
            return
        await self.delete_last_output(message.author.id)

    async def send_howto(self, ctx):
        languages = sorted(set(self.languages.values()))

        run_instructions = (
            '**Here are my supported languages:**\n'
            + ', '.join(languages) +
            '\n\n**You can run code like this:**\n'
            '/run <language>\ncommand line parameters (optional) - 1 per line\n'
            '\\`\\`\\`\nyour code\n\\`\\`\\`\n'
        )

        embed = Embed(
            title='I can execute code right here in Discord!',
            description=run_instructions,
            color=0x2ECC71
        )

        await ctx.send(embed=embed)

    @commands.command(name='eval-help')
    async def send_help(self, ctx):
        await self.send_howto(ctx)


def setup(client):
    client.add_cog(Run(client))
