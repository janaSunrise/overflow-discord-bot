import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class SuggestionConfig(DatabaseBase):
    __tablename__ = "suggestion_config"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    channel_id = Column(BigInteger, unique=True)
    submission_channel_id = Column(BigInteger, unique=True)
    anonymous = Column(Boolean, default=True)
    dm_notification = Column(Boolean, default=False)
    limit = Column(BigInteger, default=1)

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
    async def set_suggestions_channel(
            cls,
            session: AsyncSession,
            guild_id: t.Union[str, int, discord.Guild],
            channel_id: t.Union[str, int, discord.TextChannel],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        channel_id = get_datatype_int(channel_id)

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
            session: AsyncSession,
            guild_id: t.Union[str, int, discord.Guild],
            channel_id: t.Union[str, int, discord.TextChannel],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        channel_id = get_datatype_int(channel_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "submission_channel_id": channel_id},
        )
        await session.commit()

    @classmethod
    async def set_limit(
            cls,
            session: AsyncSession,
            guild_id: t.Union[str, int, discord.Guild],
            limit: int
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await session.run_sync(
            lambda session_: session_.query(cls)
                .filter_by(guild_id=guild_id)
                .update({"limit": limit})
        )
        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data


class Suggestion(DatabaseBase):
    __tablename__ = "suggestion"

    suggestion_id = Column(
        BigInteger, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    message_id = Column(BigInteger, nullable=False, unique=True)
    accepted = Column(Boolean, default=None)
    suggestion = Column(String)

    @classmethod
    async def get_config(
            cls, session: AsyncSession, suggestion_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        suggestion_id = get_datatype_int(suggestion_id)

        try:
            row = await session.run_sync(
                lambda session_: session_.query(cls)
                    .filter_by(suggestion_id=suggestion_id)
                    .first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
