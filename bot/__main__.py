import asyncio
from pathlib import Path

import discord
from discord.ext.commands import when_mentioned_or

from . import SquadBot
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


# Configure Discord gateway intents which should be used by the bot.
intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.dm_typing = False
intents.invites = False
intents.webhooks = False
intents.integrations = False

# Instantiate and configure the bot instance.
bot = SquadBot(
    loop=loop,
    command_prefix=when_mentioned_or(*config.get_prefixes()),
    case_insensitive=True,
    max_messages=10_000,
    intents=intents,
)

bot.run()
