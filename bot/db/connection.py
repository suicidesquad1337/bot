from gino import Gino

from ..utils import config


async def create_connection() -> Gino:
    db = Gino()
    await db.set_bind(config.get_database_url())

    return db


async def close_connection(db: Gino):
    await db.pop_bind().close()


async def do_migrate(db: Gino):
    await db.gino.create_all()
