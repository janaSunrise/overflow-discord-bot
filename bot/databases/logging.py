import typing as t

import discord
from sqlalchemy import BigInteger, Column
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

    @classmethod
    async def set_log_channel(
        cls,
        session: sessionmaker,
        log_type: str,
        guild: t.Union[str, int, discord.Guild],
        channel: t.Union[str, int, discord.TextChannel]
    ) -> None:
        guild = get_datatype_int(guild)
        channel = get_datatype_int(channel)

        async with session() as session:
            await on_conflict(
                session, cls,
                conflict_columns=["guild"],
                values={"guild": guild, log_type: channel}
            )
            await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
