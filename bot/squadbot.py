import discord
from discord.ext import commands
from gino import Gino

from . import db
from .utils import config


class SquadBot(commands.Bot):
    def __init__(self, db: Gino, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = db

    async def close(self):
        await db.close_connection(self.db)
        await super().close()

    def run(self):
        super().run(config.get_token())

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        print(f"ID: {self.user.id}")

    async def on_message(self, message: discord.Message):
        # Ignore messages sent by bots.
        if message.author.bot:
            return

        # Process bot commands in the message.
        ctx = await self.get_context(message)
        await self.invoke(ctx)
