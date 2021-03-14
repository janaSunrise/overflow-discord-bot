import typing as t

import discord
from sqlalchemy import Boolean, BigInteger, Column, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Starboard(DatabaseBase):
    __tablename__ = "starboard"

    id = Column(BigInteger, primary_key=True, unique=True, nullable=False, autoincrement=True)
    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    channel_id = Column(BigInteger)
    sb_emoji = Column(String)
    required_stars = Column(BigInteger, default=3)
    required_to_lose = Column(BigInteger, default=0)
    bots_in_sb = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)

    @classmethod
    async def get_config(
            cls, session: AsyncSession, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        try:
            row = await session.run_sync(
                lambda session_: session_.query(
                    cls).filter_by(guild_id=guild_id).first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data

