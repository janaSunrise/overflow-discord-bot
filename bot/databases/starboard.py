import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

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

    @classmethod
    async def clear_starboard(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        last_messages: list,
        stars: int,
    ) -> t.Any:
        query = """WITH bad_entries AS (
                       SELECT entry_id
                       FROM starrers
                       INNER JOIN starboard_message
                       ON starboard_message.id = starrers.entry_id
                       WHERE starboard_message.guild_id=:guild_id
                       AND   starboard_message.bot_message_id = ANY(:last_messages::bigint[])
                       GROUP BY entry_id
                       HAVING COUNT(*) <= :stars
                   )
                   DELETE FROM starboard_message USING bad_entries
                   WHERE starboard_message.id = bad_entries.entry_id
                   RETURNING starboard_message.bot_message_id
                """

        row = (
            await session.execute(
                text(query),
                {"guild_id": guild_id, "last_messages": last_messages, "stars": stars},
            )
        ).fetchone()

        return row

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data


class StarboardMessage(DatabaseBase):
    __tablename__ = "starboard_message"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    guild_id = Column(BigInteger, primary_key=True, nullable=False)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger, unique=True)
    user_id = Column(BigInteger)
    bot_message_id = Column(BigInteger)

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
        starrer_id: int,
    ) -> t.Any:
        query = """WITH to_insert AS (
                       INSERT INTO starboard_message AS entries (message_id, channel_id, guild_id, user_id)
                       VALUES (:message_id, :channel_id, :guild_id, :author_id)
                       ON CONFLICT (message_id) DO NOTHING
                       RETURNING entries.id
                   )
                   INSERT INTO starrers (user_id, entry_id)
                   SELECT :starrer_id, entry.id
                   FROM (
                       SELECT id FROM to_insert
                       UNION ALL
                       SELECT id FROM starboard_message WHERE message_id=:message_id
                       LIMIT 1
                   ) AS entry
                   RETURNING entry_id;
                """

        row = (
            await session.execute(
                text(query),
                {
                    "message_id": message_id,
                    "channel_id": channel_id,
                    "guild_id": guild_id,
                    "author_id": author_id,
                    "starrer_id": starrer_id,
                },
            )
        ).fetchone()

        return row

    @classmethod
    async def get_starboard_message(
        cls,
        session: AsyncSession,
        guild_id: t.Union[int, str, discord.Guild],
        message: t.Union[int, str, discord.Message],
    ) -> t.Any:
        query = """SELECT entry.channel_id,
                          entry.message_id,
                          entry.bot_message_id,
                          COUNT(*) OVER(PARTITION BY entry_id) AS "Stars"
                   FROM starrers
                   INNER JOIN starboard_message entry
                   ON entry.id = starrers.entry_id
                   WHERE entry.guild_id=:guild_id
                   AND (entry.message_id=:message OR entry.bot_message_id=:message)
                   LIMIT 1
                """

        row = (
            await session.execute(
                text(query), {"guild_id": guild_id, "message": message}
            )
        ).fetchone()

        return row

    @classmethod
    async def get_starboard_message_author(
        cls, session: AsyncSession, message: t.Union[int, str, discord.Message]
    ) -> t.Any:
        query = """SELECT starrers.user_id
                   FROM starrers
                   INNER JOIN starboard_message entry
                   ON entry.id = starrers.entry_id
                   WHERE entry.message_id = :message OR entry.bot_message_id = :message
                """

        row = (await session.execute(text(query), {"message": message})).fetchone()

        return row

    @classmethod
    async def update_starboard_message_set_null(
        cls,
        session: AsyncSession,
        id: int,
    ) -> None:
        await session.run_sync(
            lambda session_: session_.query(cls)
            .filter_by(id=id)
            .update({"bot_message_id": None})
        )
        await session.commit()

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
        await session.commit()

    @classmethod
    async def delete_starboard_message_by_id(
        cls,
        session: AsyncSession,
        id: int,
    ) -> None:
        row = await session.run_sync(
            lambda session_: session_.query(cls).filter_by(id=id).first()
        )

        await session.run_sync(lambda session_: session_.delete(row))

        await session.commit()

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

        return row.fetchall().dict()

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
    async def get_starrers_count(
        cls, session: AsyncSession, entry_id: int
    ) -> t.Optional[dict]:
        try:
            row = await session.run_sync(
                lambda session_: session_.query(func.count("*"))
                .select_from(cls)
                .filter_by(entry_id=entry_id)
            )
        except NoResultFound:
            return None

        if row is not None:
            print(row)
            return row.dict()

    @classmethod
    async def delete_star_entry_id(
        cls,
        session: AsyncSession,
        message_id: t.Union[str, int, discord.Message],
        starrer_id: int,
    ) -> t.Any:
        query = """DELETE FROM starrers USING starboard_message entry
                   WHERE entry.message_id=:message_id
                   AND   entry.id=starrers.entry_id
                   AND   starrers.user_id=:starrer_id
                   RETURNING starrers.entry_id, entry.bot_message_id
                """

        row = (
            await session.execute(
                text(query), {"message_id": message_id,
                              "starrer_id": starrer_id}
            )
        ).fetchone()
        await session.commit()

        return row

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
