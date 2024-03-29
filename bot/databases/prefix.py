import typing as t

from sqlalchemy import BigInteger, Column, String, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, get_datatype_int, on_conflict


class Prefix(DatabaseBase):
    __tablename__ = "prefixes"

    context_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    prefix = Column(String, nullable=False)

    @classmethod
    async def get_prefixes(cls, session: sessionmaker) -> t.Optional[list]:
        async with session() as session:
            try:
                rows = (await session.execute(select(cls))).scalars().all()
            except NoResultFound:
                return []

            return [row.dict() for row in rows]

    @classmethod
    async def set_prefix(
        cls, session: sessionmaker, context_id: t.Union[int, str], prefix: str
    ) -> None:
        context_id = get_datatype_int(context_id)

        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["context_id"],
                values={"context_id": context_id, "prefix": prefix},
            )
            await session.commit()
