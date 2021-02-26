from sqlalchemy import BigInteger, Column, Integer

from bot.databases import DatabaseBase


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

    __tablename__ = "link_lock"

    guild = Column(BigInteger, primary_key=True, nullable=False, unique=True)
    lock_code = Column(Integer, nullable=False)
