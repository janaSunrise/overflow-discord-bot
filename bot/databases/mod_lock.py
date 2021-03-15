import typing as t

import discord
from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class ModLock(DatabaseBase):
    """
    This is the database table for mod locking.

    Moderation locking is a way to manually lock your server to stop raiders, by either kicking, or banning them on
    join.

    Here are the codes:
    `0` - Lock disabled
    `1` - Kick lock enabled
    `2` - Ban lock enabled
    """

    __tablename__ = "mod_lock"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    lock_code = Column(Integer, nullable=False, default=0)

    @classmethod
    async def get_config(
        cls, session: AsyncSession, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        try:
            row = await session.run_sync(
                lambda session_: session_.query(cls)
                .filter_by(guild_id=guild_id)
                .first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def set_lock(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        lock_code: int,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "lock_code": lock_code},
        )
        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
