from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from bot.databases import DatabaseBase, on_conflict, get_datatype_str


class LinkLock(DatabaseBase):
    """
    This is the database table for Link locking.

    An innovative way to stop people from sending discord invites, links, links excluding discord invites and more.

    Here are the codes:
    `0` - Lock disabled
    `1` - Discord invite lock enabled
    `2` - Link lock [excluding discord invite] enabled
    `3` - Link lock and discord invite lock enabled.
    """
    __tablename__ = "mod_lock"

    guild = Column(String, primary_key=True, nullable=False, unique=True)
    lock_code = Column(Integer, nullable=False)
