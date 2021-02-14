import logging
import socket

import aiohttp
import discord
from discord.ext import commands

from . import db
from .utils.config import BOT_CONFIG

logger = logging.getLogger(__name__)


class SquadBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._resolver = aiohttp.AsyncResolver(self.loop)
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
            loop=self.loop,
        )
        self.session = aiohttp.ClientSession(connector=self._connector, loop=self.loop)

    async def close(self):
        await db.close_connection()
        await self.session.close()
        await super().close()

    def run(self):
        super().run(BOT_CONFIG.discord_token)

    async def on_ready(self):
        await db.init_connection()

        logger.info(f"Logged in as {self.user}")
        logger.info(f"ID: {self.user.id}")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.command:
            await self.invoke(ctx)
