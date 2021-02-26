import asyncio
import re
import typing as t

import discord


def snake_to_camel(snake: str, start_lower: bool = False) -> str:
    camel = snake.title()
    camel = re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)
    if start_lower:
        camel = re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)
    return camel


def camel_to_snake(camel: str) -> str:
    snake = re.sub(r"([a-zA-Z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", camel)
    snake = re.sub(r"([a-z0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    return snake.lower()


def format_time(time):
    hours, remainder = divmod(time / 1000, 3600)
    minutes, seconds = divmod(remainder, 60)

    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def progress_bar(current, total):
    barsize = 12
    num = int(current / total * barsize)
    return "▬" * num + "▭" + "―" * (barsize - num)


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


async def confirmation(
    ctx,
    description: str,
    title: str,
    color=discord.Color.blurple(),
    footer: t.Optional[str] = None,
):
    emojis = {"✅": True, "❌": False}

    embed = discord.Embed(title=title, description=description, color=color)

    if footer is not None:
        embed.set_footer(text=footer)

    message = await ctx.send(embed=embed)
    user = ctx.author

    for emoji in emojis:
        await message.add_reaction(emoji)

    try:
        reaction, user = await self.wait_for(
            "reaction_add",
            check=lambda r, u: (r.message.id == message.id)
            and (u.id == user.id)
            and (r.emoji in emojis),
            timeout=30,
        )
    except asyncio.TimeoutError:
        confirmed = None
        return
    finally:
        try:
            await message.clear_reactions()
            await message.delete()
        except discord.Forbidden:
            pass

    confirmed = emojis[reaction.emoji]
    return confirmed
