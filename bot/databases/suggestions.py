import typing as t

from discord import Guild
from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int


class SuggestionID(DatabaseBase):
    __tablename__ = "suggestion_id"

    guild_id = Column(BigInteger, primary_key=True,
                        nullable=False, unique=True)
    next_id = Column(Integer, default=0)

    @classmethod
    async def get_next_id(cls, session: AsyncSession, guild: t.Union[int, Guild]) -> int:
        guild_id = get_datatype_int(guild)

        row = await session.run_sync(lambda session: session.query(cls).filter_by(guild_id=guild_id).first())

        row.next_id += 1
        next_id = row.next_id

        await session.commit()
        return next_id
