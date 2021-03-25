import typing as t

import discord
from sqlalchemy import BigInteger, Column, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Announcements(DatabaseBase):
    __tablename__ = "announcements"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    channel_id = Column(BigInteger)
    role_id = Column(BigInteger)

    @classmethod
    async def get_announcement_role(
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
    async def get_announcement_channel(
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
    async def set_announcement_role(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        role_id: t.Union[str, int, discord.Role],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        role_id = get_datatype_int(role_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "role_id": role_id},
            )
            await session.commit()

    @classmethod
    async def set_announcement_channel(
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

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key)
                for key in self.__table__.columns.keys()}
        return data
