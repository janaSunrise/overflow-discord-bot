import typing as t

from discord import Color, Embed
from discord.ext.commands import Context
from discord.ext.menus import ListPageSource, Menu, MenuPages


class EmbedPages(ListPageSource):
    def __init__(self, embeds: t.List[Embed], embeds_per_page: int = 1):
        self.embeds = embeds
        super().__init__(embeds, per_page=embeds_per_page)

    async def format_page(self, menu: Menu, embed: Embed) -> Embed:
        """Return the stored embed for current page."""
        return embed

    async def start(self, ctx: Context, **menupages_kwargs) -> None:
        pages = MenuPages(
            source=self,
            **menupages_kwargs
        )
        await pages.start(ctx)


class SauceSource(ListPageSource):
    """Source for the sauce command."""
    async def format_page(self, menu: Menu, page: str):
        """Format the page of code."""
        max_pages = self.get_max_pages()
        embed = Embed(
            description=page,
            colour=Color.purple()
        )
        if max_pages > 1:
            embed.set_footer(text=f"Page {menu.current_page + 1}/{max_pages}")
        return embed
