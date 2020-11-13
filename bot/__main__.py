import discord
from discord.ext.commands import when_mentioned_or

from . import SquadBot

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
    command_prefix=when_mentioned_or("!"),  # TODO: Prefix from config.
    case_insensitive=True,
    max_messages=10_000,
    intents=intents,
)

bot.run()
