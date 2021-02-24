import asyncio
import contextlib
import datetime

import discord
from discord.ext.commands import Cog, Context, group, has_permissions

from bot import Bot

ROLE_SET = ":white_check_mark: The birthday role on **{s}** has been set to: **{r}**."
BDAY_INVALID = ":x: The birthday date you entered is invalid. It must be `MM-DD`."
BDAY_SET = ":white_check_mark: Your birthday has been set to: **{}**."
CHANNEL_SET = ":white_check_mark: The channel for announcing birthdays on **{s}** has been set to: **{c}**."
BDAY_REMOVED = ":put_litter_in_its_place: Your birthday has been removed."


class Birthday(Cog):
    """Announces birthday, and gives roles as configured and wishes too."""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bday_loop = asyncio.ensure_future(self.initialise())

    def __unload(self) -> None:
        self.bday_loop.cancel()

    async def load_data(self) -> None:
        pass

    async def save_data(self) -> None:
        pass

    async def initialise(self) -> None:
        await self.bot.wait_until_ready()

        with contextlib.suppress(RuntimeError):
            while self == self.bot.get_cog(self.__class__.__name__):
                now = datetime.datetime.utcnow()
                tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

                await asyncio.sleep((tomorrow - now).total_seconds())

                self.clean_yesterday_bdays()
                self.do_today_bdays()
                self.save_data()

    @group(aliases=["bday"], invoke_without_command=True)
    async def birthday(self, ctx: Context) -> None:
        """Birthday setup commands group."""
        await ctx.send_help(ctx.command)
