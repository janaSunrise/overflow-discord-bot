import typing as t

from sqlalchemy import Column, BigInteger, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict, get_datatype_int


class Prefix(DatabaseBase):
    __tablename__ = "prefixes"

    context_id = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    prefix = Column(String, nullable=False)

    @classmethod
    async def get_prefixes(cls, session: AsyncSession) -> t.Optional[list]:
        try:
            rows = await session.run_sync(lambda session: session.query(cls).all())
        except NoResultFound:
            return []

        return [row.dict() for row in rows]

    @classmethod
    async def set_prefix(
            cls,
            session: AsyncSession,
            context_id: t.Union[int, str],
            prefix: str
    ) -> None:
        context_id = get_datatype_int(context_id)

        await on_conflict(
            session, cls,
            conflict_columns=["context_id"],
            values={
                "context_id": context_id,
                "prefix": prefix
            }
        )
        await session.commit()

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key) for key in self.__table__.columns.keys()}
        return data

