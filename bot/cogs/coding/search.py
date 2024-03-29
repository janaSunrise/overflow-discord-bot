import os
import re
import textwrap
from typing import List

import aiohttp
import html2text
from discord import Color, Embed, utils
from discord.ext.commands import Cog, CommandError, Context, command
from discord.ext.commands.errors import CommandInvokeError

from bot import Bot, config

filter_words = config.filter_words


class SafesearchFail(CommandError):
    """Thrown when a query contains NSFW content."""


class Search(Cog):
    """Search the web for a variety of different resources."""

    def __init__(self, bot: Bot) -> None:
        # Main Stuff
        self.bot = bot
        self.emoji = "\U0001F50D"

        # Markdown converter
        self.tomd = html2text.HTML2Text()
        self.tomd.ignore_links = True
        self.tomd.ignore_images = True
        self.tomd.ignore_tables = True
        self.tomd.ignore_emphasis = True
        self.tomd.body_width = 0

    async def _search_logic(
        self, query: str, is_nsfw: bool = False, category: str = "web", count: int = 5
    ) -> list:
        """Use scrapestack and the Qwant API to find search results."""
        if not is_nsfw and filter_words.search(query):
            raise SafesearchFail("Query had NSFW.")

        base = "https://api.qwant.com/api"

        if is_nsfw:
            safesearch = "0"
        else:
            safesearch = "2"

        # Search URL Building
        search_url = (
            f"{base}/search/{category}"
            f"?count={count}"
            f"&q={query.replace(' ', '+')}"
            f"&safesearch={safesearch}"
            f"&t=web&locale=en_US&uiv=4"
        )

        # Searching
        headers = {"User-Agent": "Overflow bot"}
        async with self.bot.session.get(search_url, headers=headers) as resp:
            to_parse = await resp.json()

            return to_parse["data"]["result"]["items"]

    async def _basic_search(self, ctx: Context, query: str, category: str) -> None:
        """Basic search formatting."""
        is_nsfw = ctx.channel.is_nsfw() if hasattr(ctx.channel, "is_nsfw") else False

        async with ctx.typing():
            try:
                results = await self._search_logic(query, is_nsfw, category)
            except SafesearchFail:
                await ctx.send(
                    f":x: Sorry {ctx.author.mention}, your message contains filtered words, I've removed this message."
                )
                return await ctx.message.delete()
            count = len(results)

            # Ignore markdown when displaying
            query_display = utils.escape_mentions(query)
            query_display = utils.escape_markdown(query_display)

            # Return if no results
            if not count:
                return await ctx.send(f"No results found for `{query_display}`.")

            # Gets the first entry's data
            first_title = self.tomd.handle(
                results[0]["title"]).rstrip("\n").strip("<>")
            first_url = results[0]["url"]
            first_desc = self.tomd.handle(results[0]["desc"]).rstrip("\n")

            # Builds the substring for each of the other result.
            other_results: List[str] = []

            for result in results[1:count]:
                title = self.tomd.handle(result["title"]).rstrip("\n")
                url = result["url"]
                other_results.append(f"**{title}**\n{url}")

            other_msg = "\n\n".join(other_results).strip()

            # Builds message
            msg = textwrap.dedent(
                f"""
                [{first_title.strip("<>")}]({first_url.strip("<>")})\n
                {first_desc}\n
                {other_msg}
                """
            )

            msg = re.sub(
                r"(https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]+\."
                r"[a-zA-Z0-9()]+\b[-a-zA-Z0-9()@:%_+.~#?&/=]*)",
                r"<\1>",
                msg,
            )

            embed = Embed(title="Search Results",
                          description=msg, color=Color.blue())
            embed.set_footer(
                text=f"Showing {count} results for {query_display}.")

            await ctx.send(embed=embed)

    @command()
    async def search(self, ctx: Context, *, query: str) -> None:
        """Search the web for results."""
        await self._basic_search(ctx, query, category="web")

    @command(aliases=["sc-category", "search-cat"])
    async def search_category(self, ctx: Context, category: str, *, query: str) -> None:
        """
        Search online for general results with categories specified.
        **Valid Categories:**
        - web
        - videos
        - music
        - files
        - images
        - it
        - maps
        """
        if category not in config.basic_search_categories:
            await ctx.send(
                f"Invalid Category! ```Available Categories : {', '.join(config.basic_search_categories)}```"
            )
        await self._basic_search(ctx, query, category)

    @command()
    async def anime(self, ctx: Context, *, query: str) -> None:
        """Look up anime information."""
        base = "https://kitsu.io/api/edge/"

        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    base + "anime", params={"filter[text]": query}
                ) as resp:
                    resp = await resp.json()
                    resp = resp["data"]

            query = utils.escape_mentions(query)
            query = utils.escape_markdown(query)

            if not resp:
                await ctx.send(f"No results for `{query}`.")
                return

            anime = resp[0]
            title = f'{anime["attributes"]["canonicalTitle"]}'
            anime_id = anime["id"]
            url = f"https://kitsu.io/anime/{anime_id}"
            thing = (
                ""
                if not anime["attributes"]["endDate"]
                else f' to {anime["attributes"]["endDate"]}'
            )

            embed = Embed(
                title=f"{title}",
                description=anime["attributes"]["synopsis"][0:425] + "...",
                color=ctx.author.color,
                rl=url,
            )
            embed.add_field(
                name="Average Rating", value=anime["attributes"]["averageRating"]
            )
            embed.add_field(
                name="Popularity Rank", value=anime["attributes"]["popularityRank"]
            )
            embed.add_field(name="Age Rating",
                            value=anime["attributes"]["ageRating"])
            embed.add_field(name="Status", value=anime["attributes"]["status"])
            embed.add_field(
                name="Aired", value=f"{anime['attributes']['startDate']}{thing}"
            )
            embed.add_field(name="Episodes",
                            value=anime["attributes"]["episodeCount"])
            embed.add_field(name="Type", value=anime["attributes"]["showType"])
            embed.set_thumbnail(
                url=anime["attributes"]["posterImage"]["original"])
            embed.set_footer(
                text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url
            )

            try:
                await ctx.send(f"**{title}** - <{url}>", embed=embed)
            except Exception:
                aired = f"{anime['attributes']['startDate']}{thing}"
                template = textwrap.dedent(
                    f"""
                    ```
                    url: {url}
                    Title: {title}
                    Average Rating: {anime["attributes"]["averageRating"]}
                    Popularity Rank: {anime["attributes"]["popularityRank"]}
                    Age Rating: {anime["attributes"]["ageRating"]}
                    Status: {anime["attributes"]["status"]}
                    Aired: {aired}
                    Type: {anime['attributes']["showType"]}
                    ```
                    """
                )
                await ctx.send(template)

    @command()
    async def manga(self, ctx: Context, *, query: str) -> None:
        """Look up manga information."""
        base = "https://kitsu.io/api/edge/"

        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    base + "manga", params={"filter[text]": query}
                ) as resp:
                    resp = await resp.json()
                    resp = resp["data"]

            query = utils.escape_mentions(query)
            query = utils.escape_markdown(query)

            if not resp:
                await ctx.send(f"No results for `{query}`.")
                return

            manga = resp[0]
            title = f'{manga["attributes"]["canonicalTitle"]}'
            manga_id = manga["id"]
            url = f"https://kitsu.io/manga/{manga_id}"

            embed = Embed(
                title=title,
                description=manga["attributes"]["synopsis"][0:425] + "...",
                color=ctx.author.color,
                url=url,
            )

            if manga["attributes"]["averageRating"]:
                embed.add_field(
                    name="Average Rating", value=manga["attributes"]["averageRating"]
                )

            embed.add_field(
                name="Popularity Rank", value=manga["attributes"]["popularityRank"]
            )

            if manga["attributes"]["ageRating"]:
                embed.add_field(
                    name="Age Rating", value=manga["attributes"]["ageRating"]
                )

            embed.add_field(name="Status", value=manga["attributes"]["status"])
            thing = (
                ""
                if not manga["attributes"]["endDate"]
                else f' to {manga["attributes"]["endDate"]}'
            )
            embed.add_field(
                name="Published", value=f"{manga['attributes']['startDate']}{thing}"
            )

            if manga["attributes"]["chapterCount"]:
                embed.add_field(
                    name="Chapters", value=manga["attributes"]["chapterCount"]
                )

            embed.add_field(
                name="Type", value=manga["attributes"]["mangaType"])
            embed.set_thumbnail(
                url=manga["attributes"]["posterImage"]["original"])

            try:
                await ctx.send(f"**{title}** - <{url}>", embed=embed)
            except Exception:
                aired = f"{manga['attributes']['startDate']}{thing}"
                template = textwrap.dedent(
                    f"""
                    ```
                    url: {url}
                    Title: {title}
                    Average Rating: {manga["attributes"]["averageRating"]}
                    Popularity Rank: {manga["attributes"]["popularityRank"]}
                    Age Rating: {manga["attributes"]["ageRating"]}
                    Status: {manga["attributes"]["status"]}
                    Aired: {aired}
                    Type: {manga['attributes']["showType"]}
                    ```
                    """
                )
                await ctx.send(template)

    @command()
    async def weather(self, ctx: Context, *, city: str = None) -> None:
        """Sends current weather in the given city name. eg. `weather london`"""
        try:
            url_formatted_city = city.replace(" ", "-")
        except CommandInvokeError:
            await ctx.send("You didn't provide a city")

        weather_api_key = os.getenv("WEATHER_API_KEY")

        if weather_api_key is None:
            await ctx.send("Fetch Error!")
            return

        weather_lookup_url = f"https://api.openweathermap.org/data/2.5/weather?q={url_formatted_city}" \
                             f"&appid={weather_api_key}"

        async with self.bot.session.get(weather_lookup_url) as resp:
            data = await resp.json()

        if data["cod"] == "401":
            await ctx.send("Invalid API key")
            return

        if data["cod"] == "404":
            await ctx.send("Invalid city name")
            return

        weather_embed = Embed(
            title=f"Current Weather in {city.capitalize()}", color=Color.blue()
        )

        longtitude = data["coord"]["lon"]
        lattitude = data["coord"]["lat"]

        weather_embed.add_field(
            name="❯❯ Coordinates",
            value=f"**Longtitude: **`{longtitude}`\n**Latittude: **`{lattitude}`",
        )

        actual_temp = round(data["main"]["temp"] / 10, 1)
        feels_like = round(data["main"]["feels_like"] / 10, 1)
        weather_embed.add_field(
            name="❯❯ Temperature",
            value=f"**Temperature: **`{actual_temp}°C`\n**Feels Like: **`{feels_like}°C`",
        )

        wind_speed = data["wind"]["speed"]
        wind_direction = data["wind"]["deg"]
        weather_embed.add_field(
            name="❯❯ Wind",
            value=f"**Speed: **`{wind_speed}km/h`\n**Direction: **`{wind_direction}°`",
        )

        visibility = round(data["visibility"] / 1000, 2)
        humidity = data["main"]["humidity"]
        weather_description = data["weather"][0]["description"]
        weather_embed.add_field(
            name="❯❯ Miscellaneous",
            value=f"**Humidity: **`{humidity}%`\n**Visibility: **`{visibility}km`"
            f"\n**Weather Summary: **`{weather_description}`",
        )

        states = ["wind", "partly", "cloud", "snow", "rain"]
        for state in states:
            if state in weather_description:
                weather_embed.set_image(url=config.WEATHER_ICONS[state])
                break
        else:
            weather_embed.set_image(url=config.WEATHER_ICONS["sun"])

        await ctx.send(embed=weather_embed)
