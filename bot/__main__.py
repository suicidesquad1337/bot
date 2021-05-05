import asyncio
from pathlib import Path

import discord
from discord.ext.commands import when_mentioned_or

from . import SquadBot
from .logging import log
from .utils.config import BOT_CONFIG

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
finally:
    loop = asyncio.get_event_loop()

ROOT = Path(__file__).parent.parent

EXTENSIONS = ("bot.cogs.moderation", "bot.cogs.invite_tracker")


# Configure Discord gateway intents which should be used by the bot.
# See https://discordpy.readthedocs.io/en/stable/api.html#discord.Intents
intents = discord.Intents.default()

intents.bans = True
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.emojis = False
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_typing = False
intents.guilds = True
intents.integrations = False
intents.invites = True
intents.members = True
intents.messages = True
intents.presences = False
intents.reactions = False
intents.typing = False
intents.voice_states = False
intents.webhooks = True

# Instantiate and configure the bot instance.
bot = SquadBot(
    loop=loop,
    command_prefix=when_mentioned_or(*BOT_CONFIG.discord_prefixes),
    case_insensitive=True,
    max_messages=10_000,
    intents=intents,
)

for extension in EXTENSIONS:
    bot.load_extension(extension)

with log(True):
    try:
        bot.run()
    except KeyboardInterrupt:
        loop.create_task(bot.logout())
