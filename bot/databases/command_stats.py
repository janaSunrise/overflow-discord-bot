import typing as t

from sqlalchemy import BigInteger, Column, String, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from bot.databases import DatabaseBase, on_conflict


class CommandStats(DatabaseBase):
    __tablename__ = "command_stats"

    command = Column(String, primary_key=True, nullable=False, unique=True)
    usage_count = Column(BigInteger, nullable=False, default=0)

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key)
            for key in self.__table__.columns.keys()
        }
        return data

    @classmethod
    async def get_stats(cls, session: sessionmaker) -> t.List:
        async with session() as session:
            try:
                rows = await session.execute(select(cls)).all()
            except NoResultFound:
                return []

            return [row.dict() for row in rows]

    @classmethod
    async def get_command_stats(
        cls, session: sessionmaker, command_name: str
    ) -> t.Optional[t.List[dict]]:
        async with session() as session:
            try:
                row = await session.execute(select(cls).filter_by(command=command_name)).first()
            except NoResultFound:
                return None

            if row is not None:
                return row.dict()

    @classmethod
    async def set_command_stats(
        cls, session: sessionmaker, command: str, usage_count: int
    ) -> None:
        async with session() as session:
            await on_conflict(
                session,
                cls,
                conflict_columns=["command"],
                values={"command": command, "usage_count": usage_count},
            )
            await session.commit()
