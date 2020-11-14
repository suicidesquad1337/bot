from gino import Gino

from ..utils import config

DATABASE = Gino()


async def init_connection():
    await DATABASE.set_bind(config.get_database_url())


async def close_connection():
    await DATABASE.pop_bind().close()
