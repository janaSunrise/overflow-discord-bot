import typing as t

import discord
from sqlalchemy import BigInteger, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class AutoRoles(DatabaseBase):
    __tablename__ = "autoroles"

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)

    auto_roles = Column(ARRAY(BigInteger))

    @classmethod
    async def get_roles(
        cls, session: AsyncSession, guild: t.Union[str, int, discord.Guild]
    ) -> t.Optional[dict]:
        guild = get_datatype_int(guild)

        try:
            row = await session.run_sync(
                lambda session: session.query(
                    cls).filter_by(guild=guild).first()
            )
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def set_role(
        cls,
        session: AsyncSession,
        guild: t.Union[str, int, discord.Guild],
        role: t.Union[str, int, discord.Role],
    ) -> None:
        guild = get_datatype_int(guild)
        role = get_datatype_int(role)

        await on_conflict(
            session,
            cls,
            conflict_columns=["guild"],
            values={"guild": guild, "auto_roles": role},
        )
        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key, None)
                for key in self.__table__.columns.keys()}
        return data
