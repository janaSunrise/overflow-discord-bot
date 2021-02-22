from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict, get_datatype_str


class ModLock(DatabaseBase):
    """
    This is the database table for mod locking.

    Moderation locking is a way to manually lock your server to stop raiders, by either kicking, or banning them on
    join.

    Here are the codes:
    `0` - Lock disabled
    `1` - Kick lock enabled
    `2` - Ban lock enabled
    """
    __tablename__ = "mod_lock"

    guild = Column(String, primary_key=True, nullable=False, unique=True)
    lock_code = Column(Integer, nullable=False)
