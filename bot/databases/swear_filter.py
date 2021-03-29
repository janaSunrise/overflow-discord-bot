import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, String, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class SwearFilter(DatabaseBase):
    __tablename__ = "swear_filter"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    manual_on = Column(Boolean, default=False)
    autoswear = Column(Boolean, default=False)
    notification = Column(Boolean, default=False)
    words = Column(ARRAY(String), default=[])

    @classmethod
    async def get_config(
        cls, session: sessionmaker, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            try:
                row = (
                    await session.execute(select(cls).filter_by(guild_id=guild_id))
                ).scalar_one()
            except NoResultFound:
                return None

            if row is not None:
                return row.dict()

    @classmethod
    async def set_filter_mode(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        mode: bool,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "manual_on": mode},
            )
            await session.commit()

    @classmethod
    async def set_auto_mode(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        mode: bool,
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "autoswear": mode},
            )
            await session.commit()

    @classmethod
    async def set_notification(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        mode: bool,
    ):
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "notification": mode},
            )
            await session.commit()

    @classmethod
    async def set_words(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        words: t.List[str],
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "words": words},
            )
            await session.commit()
