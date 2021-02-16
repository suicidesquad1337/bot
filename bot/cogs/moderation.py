import discord
from discord.ext import commands

from .. import SquadBot


class Moderation(commands.Cog):
    def __init__(self, bot: SquadBot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self, ctx: commands.Context, target: discord.Member, *, reason: str = ""
    ):
        """Kicks a member from the server."""
        safe_name = await commands.clean_content(escape_markdown=True).convert(
            ctx, str(target)
        )

        user_notification = (
            f"You were kicked from {ctx.guild.name} for \"{reason or 'no reason'}\"."
            "\n\nFeel free to rejoin, but mind the rules next time."
        )
        try:
            await target.send(user_notification)
        except discord.Forbidden:
            # User has DMs disabled or blocked the bot.
            pass

        await target.kick(reason=f"By {ctx.author} for {reason or 'no reason'}")
        await ctx.send(f"🥾 {safe_name} 🚪")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self, ctx: commands.Context, target: discord.Member, *, reason: str = ""
    ):
        """Bans a member from the server."""
        safe_name = await commands.clean_content(escape_markdown=True).convert(
            ctx, str(target)
        )

        user_notification = (
            f"You were banned from {ctx.guild.name} for \"{reason or 'no reason'}\"."
            "\n\nThis ban is permanent."
        )
        try:
            await target.send(user_notification)
        except discord.Forbidden:
            # User has DMs disabled or blocked the bot.
            pass

        await target.ban(
            reason=f"By {ctx.author} for {reason or 'no reason'}", delete_message_days=0
        )
        await ctx.send(f"⛔ {safe_name}")


def setup(bot: SquadBot):
    bot.add_cog(Moderation(bot))
