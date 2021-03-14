import typing as t

from discord import Guild
from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int


class SuggestionConfig(DatabaseBase):
    __tablename__ = "suggestion_config"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    channel_id = Column(BigInteger, unique=True)
    limit = Column(BigInteger)


class SuggestionUser(DatabaseBase):
    __tablename__ = "suggestion_user"
    user_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    anonymous = Column(Boolean, default=False)
    dm_notification = Column(Boolean, default=False)


class Suggestion(DatabaseBase):
    __tablename__ = "suggestion"

    suggestion_id = Column(BigInteger, primary_key=True, nullable=False, unique=True, autoincrement=True)
    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    suggestion = Column(String)
