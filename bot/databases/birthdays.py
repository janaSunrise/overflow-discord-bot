import typing as t

import discord
from sqlalchemy import Column, BigInteger, ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.mutable import MutableList

from bot.databases import DatabaseBase, on_conflict, get_datatype_int


class Birthday(DatabaseBase):
    __tablename__ = "birthday"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    channel_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    user_ids = Column(MutableList.as_mutable(ARRAY(BigInteger)))

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key) for key in self.__table__.columns.keys()}
        return data
