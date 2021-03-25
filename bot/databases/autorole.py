import typing as t

import discord
from sqlalchemy import BigInteger, Column, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class AutoRoles(DatabaseBase):
    __tablename__ = "autoroles"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    auto_roles = Column(ARRAY(BigInteger), default=[])

    @classmethod
    async def get_roles(
        cls, session: sessionmaker, guild_id: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild_id = get_datatype_int(guild_id)

        async with session() as session:
            try:
                row = (
                    await session.execute(select(cls).filter_by(guild_id=guild_id))
                ).first()
            except NoResultFound:
                return None

            if row is not None:
                return row.dict()

    @classmethod
    async def set_role(
        cls,
        session: sessionmaker,
        guild_id: t.Union[str, int, discord.Guild],
        role: t.List[t.Union[str, int, discord.Role]],
    ) -> None:
        guild_id = get_datatype_int(guild_id)
        role = [get_datatype_int(r) for r in role]

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["guild_id"],
                values={"guild_id": guild_id, "auto_roles": role},
            )
            await session.commit()
