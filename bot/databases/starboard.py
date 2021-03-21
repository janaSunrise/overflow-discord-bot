import typing as t

import discord
from sqlalchemy import (BigInteger, Boolean, Column, ForeignKey, func, insert,
                        select)
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Starboard(DatabaseBase):
    __tablename__ = "starboard"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    channel_id = Column(BigInteger, unique=True)
    required_stars = Column(BigInteger, default=3)
    required_to_lose = Column(BigInteger, default=0)
    bots_in_sb = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    on_edit = Column(Boolean, default=True)
    on_delete = Column(Boolean, default=False)

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
    async def set_starboard_channel(
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
    async def set_required_stars(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        required_stars: int,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "required_stars": required_stars},
        )
        await session.commit()

    @classmethod
    async def set_required_to_lose(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        required_to_lose: int,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id,
                    "required_to_lose": required_to_lose},
        )
        await session.commit()

    @classmethod
    async def set_on_delete(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        on_delete: bool,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "on_delete": on_delete},
        )
        await session.commit()

    @classmethod
    async def set_on_edit(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        on_edit: bool,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "on_edit": on_edit},
        )
        await session.commit()

    @classmethod
    async def set_bots_in_sb(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        bots_in_sb: bool,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "bots_in_sb": bots_in_sb},
        )
        await session.commit()

    @classmethod
    async def delete_starboard_channel(
        cls, session: AsyncSession, guild_id: t.Union[str, int, discord.Guild]
    ) -> None:
        row = await session.run_sync(
            lambda session_: session_.query(
                cls).filter_by(guild_id=guild_id).first()
        )
        await session.run_sync(lambda session_: session_.delete(row))

        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data


class StarboardMessage(DatabaseBase):
    __tablename__ = "starboard_message"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    channel_id = Column(BigInteger, unique=True)
    message_id = Column(BigInteger, unique=True)
    user_id = Column(BigInteger, unique=True)
    bot_message_id = Column(BigInteger, unique=True)

    @classmethod
    async def get_config(
        cls, session: AsyncSession, bot_message_id: t.Union[str, int, discord.Message]
    ) -> t.Optional[dict]:
        bot_message_id = get_datatype_int(bot_message_id)

        try:
            row = await session.run_sync(
                lambda session_: session_.query(cls)
                .filter_by(bot_message_id=bot_message_id)
                .first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def get_config_message_id(
        cls, session: AsyncSession, message_id: t.Union[str, int, discord.Message]
    ) -> t.Optional[dict]:
        message_id = get_datatype_int(message_id)

        try:
            row = await session.run_sync(
                lambda session_: session_.query(cls)
                .filter_by(message_id=message_id)
                .first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def get_star_entry_id(
        cls,
        session: AsyncSession,
        message_id: t.Union[str, int, discord.Message],
        channel_id: t.Union[str, int, discord.TextChannel],
        guild_id: t.Union[str, int, discord.Guild],
        author_id: t.Union[str, int, discord.User],
        starrer_id: int
    ) -> t.Any:
        query = """WITH to_insert AS (
                       INSERT INTO starboard_message AS entries (message_id, channel_id, guild_id, author_id)
                       VALUES (:message_id, :channel_id, :guild_id, :author_id)
                       ON CONFLICT (message_id) DO NOTHING
                       RETURNING entries.id
                   )
                   INSERT INTO starrers (author_id, entry_id)
                   SELECT :starrer_id, entry.id
                   FROM (
                       SELECT id FROM to_insert
                       UNION ALL
                       SELECT id FROM starboard_message WHERE message_id=:message_id
                       LIMIT 1
                   ) AS entry
                   RETURNING entry_id;
                """

        row = (await session.execute(text(query), {
            "message_id": message_id, "channel_id": channel_id, "guild_id": guild_id, "author_id": author_id,
            "starrer_id": starrer_id
        })).fetchone()

        return row

    @classmethod
    async def update_starboard_message(
        cls,
        session: AsyncSession,
        message_id: t.Union[str, int, discord.Message],
        bot_message_id: t.Union[str, int, discord.Message],
    ) -> None:
        message_id = get_datatype_int(message_id)
        bot_message_id = get_datatype_int(bot_message_id)

        await session.run_sync(
            lambda session_: session_.query(cls)
            .filter_by(message_id=message_id)
            .update({"bot_message_id": bot_message_id})
        )

    @classmethod
    async def delete_starboard_message(
        cls,
        session: AsyncSession,
        bot_message_id: t.Union[str, int, discord.Message, list],
    ) -> tuple:
        if isinstance(bot_message_id, list):
            row = await session.run_sync(
                lambda session_: session_.query(cls).filter(
                    cls.bot_message_id.any(bot_message_id).all()
                )
            )
        else:
            bot_message_id = get_datatype_int(bot_message_id)

            row = await session.run_sync(
                lambda session_: session_.query(cls)
                .filter_by(bot_message_id=bot_message_id)
                .first()
            )

        row = await session.run_sync(lambda session_: session_.delete(row))

        await session.commit()

        return row.fetchall()

    @classmethod
    async def delete_starboard_message_msg_id(
        cls,
        session: AsyncSession,
        message_id: t.Union[str, int, discord.Message, list],
    ) -> None:
        message_id = get_datatype_int(message_id)

        row = await session.run_sync(
            lambda session_: session_.query(cls)
            .filter_by(message_id=message_id)
            .first()
        )

        row = await session.run_sync(lambda session_: session_.delete(row))

        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data


class Starrers(DatabaseBase):
    __tablename__ = "starrers"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True)
    entry_id = Column(BigInteger, ForeignKey("starboard_message.id"))

    @classmethod
    async def get_starrers_count(cls, session: AsyncSession, entry_id: int) -> None:
        try:
            row = await session.run_sync(
                lambda session_: session_.query(func.count("*"))
                .select_from(cls)
                .where(entry_id == entry_id)
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
