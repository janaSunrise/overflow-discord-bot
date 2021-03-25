import typing as t

import discord
from sqlalchemy import BigInteger, Column, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Roles(DatabaseBase):
    __tablename__ = "roles"

    guild_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    mod_role = Column(ARRAY(BigInteger))
    mute_role = Column(BigInteger)
    default_role = Column(BigInteger)

    @classmethod
    async def get_roles(
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
    async def set_role(
        cls,
        session: sessionmaker,
        role_type: str,
        guild_id: t.Union[str, int, discord.Guild],
        role: t.Union[str, int, discord.Role, t.List[discord.Role]],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        role = get_datatype_int(role)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, role_type: role},
            )
            await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key, None)
            for key in self.__table__.columns.keys()
        }
        return data
