import discord
from discord.ext import commands

from . import db
from .utils.config import BOT_CONFIG


class SquadBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def close(self):
        await db.close_connection()
        await super().close()

    def run(self):
        super().run(BOT_CONFIG.config.discord_token)

    async def on_ready(self):
        # Initialize the database connection.
        await db.init_connection()

        print(f"Logged in as {self.user.name}#{self.user.discriminator}")
        print(f"ID: {self.user.id}")

    async def on_message(self, message: discord.Message):
        # Ignore messages sent by bots.
        if message.author.bot:
            return
        # Process bot commands in the message.
        ctx = await self.get_context(message)
        await self.invoke(ctx)
