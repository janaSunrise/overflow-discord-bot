import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, func, insert, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import NoResultFound
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
            cls, session: AsyncSession, entry_id: int, message_id: t.Union[str, int, discord.Message],
            author_id: t.Union[str, int, discord.User]
    ) -> t.Any:
        message_id = get_datatype_int(message_id)
        author_id = get_datatype_int(author_id)

        query_1 = select(cls.id)
        query_2 = select(cls.id).filter_by(message_id=message_id)

        union_q = query_1.union(query_2).limit(1).all()

        query = insert(Starrers).values(user_id=author_id, entry_id=entry_id).select(union_q).returning(entry_id)

        row = await session.execute(query)
        await session.commit()

        return row

    @classmethod
    async def insert_sb_entry(
            cls,
            session: AsyncSession,
            message_id: t.Union[int, str, discord.Message],
            channel_id: t.Union[int, str, discord.TextChannel],
            guild_id: t.Union[int, str, discord.Guild],
            author_id: t.Union[int, str, discord.User],
    ) -> t.Any:
        author_id = get_datatype_int(author_id)
        message_id = get_datatype_int(message_id)
        channel_id = get_datatype_int(channel_id)
        guild_id = get_datatype_int(guild_id)

        row = await session.execute(postgresql.insert(cls).values(
            user_id=author_id, message_id=message_id, guild_id=guild_id, channel_id=channel_id
        ).on_conflict_do_nothing().returning(cls.id))

        await session.commit()

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
            lambda session_: session_.query(cls).filter_by(message_id=message_id)
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
    async def get_starrers_count(
            cls,
            session: AsyncSession,
            entry_id: int
    ) -> None:
        try:
            row = await session.run_sync(
                lambda session_: session_.query(func.count("*")).select_from(cls).where(entry_id == entry_id)
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
