import re
import typing as t

import discord


def format_time(time):
    hours, remainder = divmod(time / 1000, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:.2f}{minutes:.2f}{seconds:.2f}"


async def create_urban_embed_list(results: list) -> t.List[discord.Embed]:
    BRACKETED = re.compile(r"(\[(.+?)\])")
    embeds_list = []

    def cleanup_definition(definition: str, *, regex: str = BRACKETED) -> str:
        """Cleanup the definition."""
        def repl(message) -> str:
            word = message.group(2)
            return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'

        ret = regex.sub(repl, definition)
        if len(ret) >= 2048:
            return ret[0:2000] + " [...]"
        return ret

    for res in results:
        title = res["word"]

        embed = discord.Embed(colour=0xE86222, title=title, url=res["permalink"])
        embed.set_footer(text=f'Author : {res["author"]}')
        embed.description = cleanup_definition(res["definition"])

        try:
            date = discord.utils.parse_time(res["written_on"][0:-1])
        except (ValueError, KeyError):
            pass
        else:
            embed.timestamp = date

        embeds_list.append(embed)

    return embeds_list
