from sqlalchemy import BigInteger, Column, Integer

from bot.databases import DatabaseBase


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

    guild_id = Column(BigInteger, primary_key=True,
                      nullable=False, unique=True)
    lock_code = Column(Integer, nullable=False)
