from pathlib import Path

import discord
from discord.ext.commands import when_mentioned_or

from . import SquadBot
from .utils import config

ROOT = Path(__file__).parent.parent

# Source in bot configuration variables from .env in the project root.
config.load_config(ROOT)

# Configure Discord gateway intents which should be used by the bot.
intents = discord.Intents.default()
intents.members = True
intents.typing = False
intents.dm_typing = False
intents.invites = False
intents.webhooks = False
intents.integrations = False

# Instantiate and prepare the bot instance.
bot = SquadBot(
    command_prefix=when_mentioned_or(*config.get_prefixes()),
    case_insensitive=True,
    max_messages=10_000,
    intents=intents,
)

bot.run()
