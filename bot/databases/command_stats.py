import typing as t

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict


class CommandStats(DatabaseBase):
    __tablename__ = "command_stats"

    command = Column(String, primary_key=True,
                      nullable=False, unique=True)
    usage_count = Column(BigInteger, nullable=False, default=0)

    def dict(self) -> t.Dict[str, t.Any]:
        data = {key: getattr(self, key)
                for key in self.__table__.columns.keys()}
        return data

    @classmethod
    async def get_stats(cls, session: AsyncSession) -> t.List:
        try:
            rows = await session.run_sync(lambda session: session.query(cls).all())
        except NoResultFound:
            return []

        return [row.dict() for row in rows]

    @classmethod
    async def get_command_stats(cls, session: AsyncSession, command_name: str) -> t.Optional[t.List[dict]]:
        try:
            row = await session.run_sync(lambda session: session.query(cls).filter_by(command=command_name).first())
        except NoResultFound:
            return None

        if row is not None:
            return row.dict()

    @classmethod
    async def set_command_stats(
            cls,
            session: AsyncSession,
            command: str,
            usage_count: int
    ) -> None:
        await on_conflict(
            session,
            cls,
            conflict_columns=["command"],
            values={"command": command, "usage_count": usage_count},
        )
        await session.commit()
