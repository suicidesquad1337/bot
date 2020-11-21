from gino import Gino

from ..utils.config import BOT_CONFIG

DATABASE = Gino()


async def init_connection():
    await DATABASE.set_bind(BOT_CONFIG.construct_database_url())


async def close_connection():
    await DATABASE.pop_bind().close()
