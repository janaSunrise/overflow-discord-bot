import typing as t
from importlib import import_module

import discord
import sqlalchemy as alchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base, declared_attr
from sqlalchemy.sql.base import ImmutableColumnCollection

from bot.utils.utils import camel_to_snake


# Custom database base
class CustomMeta(DeclarativeMeta):
    __table__: alchemy.Table

    @property
    def columns(self) -> ImmutableColumnCollection:
        return self.__table__.columns()


class CustomBase:
    __table__: alchemy.Table

    if t.TYPE_CHECKING:
        __tablename__: str
    else:
        @declared_attr
        def __tablename__(self) -> str:
            return camel_to_snake(self.__name__)

    def dict(self) -> t.Dict[str, t.Any]:
        data = {
            key: getattr(self, key) for key in self.__table__.columns.keys()
        }
        return data


_Base = declarative_base(cls=CustomBase, metaclass=CustomMeta)


if t.TYPE_CHECKING:
    class DatabaseBase(_Base, CustomBase, metaclass=CustomMeta):
        __table__: alchemy.Table
        __tablename__: str

        metadata: alchemy.MetaData
        columns: ImmutableColumnCollection
else:
    DatabaseBase = _Base


# -- Get tables into scope --
def bring_databases_into_scope() -> t.List:
    from bot.core import loader

    loaded_tables = []

    for table in loader.DATABASES:
        imported_table = import_module(table)
        loaded_tables.append(imported_table)

    return loaded_tables


# Utility methods
def get_datatype_int(
    datatype: t.Union[
        int,
        str,
        discord.TextChannel,
        discord.Guild,
        discord.Role,
        discord.Member,
        discord.User,
    ]
) -> int:
    if isinstance(
        datatype,
        (
            discord.TextChannel,
            discord.Guild,
            discord.Role,
            discord.Member,
            discord.User,
        ),
    ):
        datatype = int(datatype.id)

    if isinstance(datatype, str):
        datatype = int(datatype)

    return datatype


async def on_conflict(
    session: AsyncSession, model: DatabaseBase, conflict_columns: list, values: dict
) -> None:
    table = model.__table__
    stmt = postgresql.insert(table)

    affected_columns = {
        col.name: col
        for col in stmt.excluded
        if col.name in values and col.name not in conflict_columns
    }

    if not affected_columns:
        raise ValueError("Couldn't find any columns to update.")

    stmt = stmt.on_conflict_do_update(index_elements=conflict_columns, set_=affected_columns)

    await session.execute(stmt, values)
