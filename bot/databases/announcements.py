import typing as t

import discord
from sqlalchemy import Column, BigInteger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict, get_datatype_int


class Announcements(DatabaseBase):
    __tablename__ = "announcements"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    role_id = Column(BigInteger, nullable=False)

    @classmethod
    async def get_announcement_role(
            cls, session: AsyncSession, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        try:
            row = await session.run_sync(lambda session: session.query(cls).filter_by(guild_id=guild_id).first())
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def set_announcement_role(
            cls,
            session: AsyncSession,
            guild_id: t.Union[str, int, discord.Guild],
            role_id: t.Union[str, int, discord.TextChannel]
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        role_id = get_datatype_int(role_id)

        await on_conflict(
            session, cls,
            conflict_columns=["guild_id"],
            values={
                "guild_id": guild_id,
                "role_id": role_id
            }
        )
        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key) for key in self.__table__.columns.keys()}
        return data
