import typing as t

import discord
from sqlalchemy import BigInteger, Boolean, Column, String, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Logging(DatabaseBase):
    __tablename__ = "logging"

    guild_id = Column(
        BigInteger, primary_key=True,
        nullable=False, unique=True
    )
    server_log = Column(BigInteger)
    mod_log = Column(BigInteger)
    message_log = Column(BigInteger)
    member_log = Column(BigInteger)
    join_log = Column(BigInteger)
    voice_log = Column(BigInteger)

    @classmethod
    async def get_config(
        cls, session: sessionmaker, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
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

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
