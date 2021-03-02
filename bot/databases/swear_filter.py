import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class SwearFilter(DatabaseBase):
    __tablename__ = "swear_filter"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    manual_on = Column(Boolean, nullable=False, default=False)
    autoswear = Column(Boolean, nullable=False, default=False)
    notification = Column(Boolean, nullable=False, default=False)
    words = Column(ARRAY(String), nullable=False, default=[])

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data

    @classmethod
    async def get_config(
        cls, session: AsyncSession, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        try:
            row = await session.run_sync(
                lambda session: session.query(
                    cls).filter_by(guild_id=guild_id).first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def set_filter_mode(
        cls,
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        mode: bool,
    ):
        guild_id = get_datatype_int(guild_id)

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
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        mode: bool,
    ):
        guild_id = get_datatype_int(guild_id)

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
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        mode: bool,
    ):
        guild_id = get_datatype_int(guild_id)

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
        session: AsyncSession,
        guild_id: t.Union[str, int, discord.Guild],
        words: t.List[str],
    ) -> None:
        guild_id = get_datatype_int(guild_id)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild_id"],
            values={"guild_id": guild_id, "words": words},
        )
        await session.commit()
