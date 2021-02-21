import typing as t

import discord
from sqlalchemy import Column, BigInteger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict


class HackernewsFeed(DatabaseBase):
    __tablename__ = "hackernews_feed"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    channel_id = Column(BigInteger, nullable=False)

    @classmethod
    async def get_feed_channel(cls, session: AsyncSession, guild_id: int) -> t.Optional[dict]:
        try:
            row = await session.run_sync(lambda session: session.query(cls).filter_by(guild_id=guild_id).first())
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
    async def set_feed_channel(cls, session: AsyncSession, guild_id: int, channel_id: int) -> None:
        await on_conflict(
            session, cls,
            conflict_columns=["guild_id"],
            values={
                "guild_id": guild_id,
                "channel_id": channel_id
            }
        )
        await session.commit()

    @classmethod
    async def remove_feed_channel(cls, session: AsyncSession, guild_id: int) -> None:
        row = await session.run_sync(
            lambda session: session.query(cls).filter_by(guild_id=guild_id).first()
        )
        await session.run_sync(lambda session: session.delete(row))
        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key) for key in self.__table__.columns.keys()}
        return data
