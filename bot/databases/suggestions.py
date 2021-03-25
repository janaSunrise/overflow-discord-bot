import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, String, insert, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class SuggestionConfig(DatabaseBase):
    __tablename__ = "suggestion_config"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    channel_id = Column(BigInteger, unique=True)
    submission_channel_id = Column(BigInteger, unique=True)
    anonymous = Column(Boolean, default=True)
    dm_notification = Column(Boolean, default=False)
    limit = Column(BigInteger, default=1)

    @classmethod
    async def get_config(
        cls, session: sessionmaker, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            try:
                row = (await session.execute(select(cls).filter_by(guild_id=guild_id))).first()
            except NoResultFound:
                return None

            if row is not None:
                return row.dict()

    @classmethod
    async def set_suggestions_channel(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        channel_id: t.Union[str, int, discord.TextChannel],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        channel_id = get_datatype_int(channel_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "channel_id": channel_id},
            )
            await session.commit()

    @classmethod
    async def set_submission_channel(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        channel_id: t.Union[str, int, discord.TextChannel],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        channel_id = get_datatype_int(channel_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={
                    "guild_id": guild_id,
                    "submission_channel_id": channel_id
                },
            )
            await session.commit()

    @classmethod
    async def set_limit(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        limit: int,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "limit": limit},
            )
            await session.commit()

    @classmethod
    async def set_dm(
        cls, session: sessionmaker, guild_id: t.Union[str, int, discord.Guild], dm: bool
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "dm_notification": dm},
            )
            await session.commit()

    @classmethod
    async def set_anonymous(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        anonymous: bool,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "anonymous": anonymous},
            )
            await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key, None)
            for key in self.__table__.columns.keys()
        }
        return data


class SuggestionUser(DatabaseBase):
    __tablename__ = "suggestion_user"

    user_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    anonymous = Column(Boolean, default=False)
    dm_notification = Column(Boolean, default=False)

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key, None)
            for key in self.__table__.columns.keys()
        }
        return data

    @classmethod
    async def get_config(
            cls, session: sessionmaker, user_id: t.Union[str, int, discord.User]
    ) -> t.Optional[dict]:
        user_id = get_datatype_int(user_id)

        async with session() as session:
            try:
                row = (await session.execute(select(cls).filter_by(user_id=user_id))).first()
            except NoResultFound:
                return None

            if row is not None:
                return row.dict()

    @classmethod
    async def set_user(
        cls,
        session: sessionmaker,
        user_id: t.Union[str, int, discord.Guild],
    ) -> None:
        user_id = get_datatype_int(user_id)

        async with session() as session:
            await session.execute(insert(cls).values(user_id=user_id))
            await session.commit()

    @classmethod
    async def set_dm(
        cls, session: sessionmaker, user_id: t.Union[str, int, discord.User], dm: bool
    ) -> None:
        user_id = get_datatype_int(user_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["user_id"],
                values={"user_id": user_id, "dm_notification": dm},
            )
            await session.commit()

    @classmethod
    async def set_anonymous(
        cls,
        session: sessionmaker,
        user_id: t.Union[str, int, discord.User],
        anonymous: bool,
    ) -> None:
        user_id = get_datatype_int(user_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["user_id"],
                values={"user_id": user_id, "anonymous": anonymous},
            )
            await session.commit()


class Suggestion(DatabaseBase):
    __tablename__ = "suggestion"

    suggestion_id = Column(BigInteger, primary_key=True, nullable=False, unique=True, autoincrement=True)
    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    message_id = Column(BigInteger, nullable=False, unique=True)
    accepted = Column(Boolean, default=None)
    suggestion = Column(String)

    @classmethod
    async def get_config(
        cls, session: sessionmaker, suggestion_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        suggestion_id = get_datatype_int(suggestion_id)

        async with session() as session:
            try:
                row = (await session.execute(select(cls).filter_by(suggestion_id=suggestion_id))).first()
            except NoResultFound:
                return None

            if row is not None:
                return row.dict()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key, None)
            for key in self.__table__.columns.keys()
        }
        return data
