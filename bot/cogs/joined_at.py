import discord
from discord.ext import commands

from ..squadbot import SquadBot


class JoinedAt(commands.Cog):
    def __init__(self, bot: SquadBot):
        self.bot = bot

    @commands.guild_only()
    @commands.command("joined_at", aliases=["joined", "jat", "j"])
    async def joined_at(self, ctx: commands.Context, member: discord.Member = None):
        """Display the join date of you or a member"""
        if member:
            await ctx.send(
                f"{member} joined at {member.joined_at.strftime('%d/%m/%Y %H:%M:%S')}."
            )
        else:
            await ctx.send(
                f"You joined at {ctx.author.joined_at.strftime('%d/%m/%Y %H:%M:%S')}."
            )


def setup(bot: SquadBot):
    bot.add_cog(JoinedAt(bot))
