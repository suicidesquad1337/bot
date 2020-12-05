import discord
from discord.ext import commands

from ..db.schema import Autistenpunkte
from ..utils.config import BOT_CONFIG


class Autistenchecker(commands.Cog):
    # returns 0 if the message contains no autisten emotes otherwise the total of
    # autisten emotes.
    @staticmethod
    async def contains_autisten_emotes(msg: str) -> int:
        total_found = 0
        for emote in BOT_CONFIG.smaland_banned_custom_emotes:
            total_found += msg.count(emote)
        for emote in BOT_CONFIG.sum_banned_emojis():
            total_found += msg.count(emote)
        return total_found

    async def autisten_emote_check(self, msg: discord.Message) -> None:
        if msg.channel.id in BOT_CONFIG.smaland_autistenpunkte_ignored_channels:
            return
        if (c := await self.contains_autisten_emotes(msg.content)) > 0:
            await Autistenpunkte.insert_or_increase_score(msg.author, c)
            await msg.delete()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        await self.autisten_emote_check(msg)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after: discord.Message):  # noqa
        await self.autisten_emote_check(after)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if (
            reaction.message.channel.id
            in BOT_CONFIG.smaland_autistenpunkte_ignored_channels
        ):
            return
        if (
            reaction.emoji in BOT_CONFIG.smaland_banned_custom_emotes
            or reaction.emoji in BOT_CONFIG.sum_banned_emojis()
        ):
            await Autistenpunkte.insert_or_increase_score(user, 1)
            await reaction.remove(user)
