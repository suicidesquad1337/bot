import asyncio
from pathlib import Path

import discord
from discord.ext.commands import when_mentioned_or
from gino import Gino

from . import SquadBot, db
from .utils import config

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
finally:
    loop = asyncio.get_event_loop()

ROOT = Path(__file__).parent.parent

# Source in bot configuration variables from .env in the project root.
config.load_config(ROOT)


async def initialize_database() -> Gino:
    connection = await db.create_connection()
    await db.do_migrate(connection)

    return connection


# Configure Discord gateway intents which should be used by the bot.
intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.dm_typing = False
intents.invites = False
intents.webhooks = False
intents.integrations = False

# Instantiate and configure the bot instance.
database = loop.run_until_complete(initialize_database())
bot = SquadBot(
    database,
    command_prefix=when_mentioned_or(*config.get_prefixes()),
    case_insensitive=True,
    max_messages=10_000,
    intents=intents,
)

bot.run()
