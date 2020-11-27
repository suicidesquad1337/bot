import discord
from discord.ext import commands

from ..db.schema import Autistenpunkte
from ..utils.config import BOT_CONFIG


class Autistenchecker(commands.Cog):
    # returns 0 if the message contains no autisten emotes otherwise the total of
    # autisten emotes.
    @staticmethod
    async def contains_autisten_emotes(msg: discord.Message) -> int:
        # TODO: implement unicode check
        total_found = 0
        for emote in BOT_CONFIG.smaland_banned_custom_emotes:
            total_found += msg.content.count(emote)
        return total_found

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.channel.id in BOT_CONFIG.smaland_autistenpunkte_ignored_channels:
            return
        if (c := await self.contains_autisten_emotes(msg)) > 0:
            await Autistenpunkte.insert_or_increase_score(msg.author, c)
