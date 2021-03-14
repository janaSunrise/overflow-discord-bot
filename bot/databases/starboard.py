import typing as t

import discord
from sqlalchemy import Boolean, BigInteger, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Starboard(DatabaseBase):
    __tablename__ = "starboard"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    channel_id = Column(BigInteger)
    sb_emoji = Column(String)
    required_stars = Column(BigInteger, default=3)
    required_to_lose = Column(BigInteger, default=1)
    bots_in_sb = Column(Boolean, default=False)

