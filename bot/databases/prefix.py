import typing as t

import discord
from sqlalchemy import Column, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict, get_datatype_str


class Prefix(DatabaseBase):
    __tablename__ = "prefixes"

    context = Column(String, primary_key=True, nullable=False, unique=True)
    channel = Column(String, nullable=False)

    @classmethod
    async def get_prefixes(cls, session: AsyncSession) -> t.Optional[list]:
        try:
            rows = await session.run_sync(lambda session: session.query(cls).all())
        except NoResultFound:
            return []

        return [row.dict() for row in rows]

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: int(getattr(self, key)) for key in self.__table__.columns.keys()
        }
        return data

