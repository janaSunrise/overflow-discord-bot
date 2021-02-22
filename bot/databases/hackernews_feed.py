import typing as t

import discord
from sqlalchemy import Column, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict, get_datatype_str


class HackernewsFeed(DatabaseBase):
    __tablename__ = "hackernews_feed"

    guild = Column(String, primary_key=True, nullable=False, unique=True)
    channel = Column(String, nullable=False)

    @classmethod
    async def get_feed_channel(cls, session: AsyncSession, guild: t.Union[str, int, discord.Guild]) -> t.Optional[dict]:
        guild = get_datatype_str(guild)
        
        try:
            row = await session.run_sync(lambda session: session.query(cls).filter_by(guild=guild).first())
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def get_feed_channels(cls, session: AsyncSession) -> t.Optional[list]:
        try:
            rows = await session.run_sync(lambda session: session.query(cls).all())
        except NoResultFound:
            return []

        return [row.dict() for row in rows]

    @classmethod
    async def set_feed_channel(
            cls,
            session: AsyncSession,
            guild: t.Union[str, int, discord.Guild],
            channel: t.Union[str, int, discord.TextChannel]
    ) -> None:
        guild = get_datatype_str(guild)
        channel = get_datatype_str(channel)

        await on_conflict(
            session, cls,
            conflict_columns=["guild"],
            values={
                "guild": guild,
                "channel": channel
            }
        )
        await session.commit()

    @classmethod
    async def remove_feed_channel(cls, session: AsyncSession, guild: t.Union[str, int, discord.Guild]) -> None:
        guild = get_datatype_str(guild)

        row = await session.run_sync(lambda session: session.query(cls).filter_by(guild=guild).first())
        await session.run_sync(lambda session: session.delete(row))

        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key) for key in self.__table__.columns.keys()
        }
        return data
