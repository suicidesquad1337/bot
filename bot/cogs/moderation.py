import discord
from discord.ext import commands

from .. import SquadBot
from ..utils.checks import is_kerkermeister


class CheckedMember(commands.MemberConverter):
    async def convert(self, ctx, argument):
        member = await super().convert(ctx, argument)
        safe_name = await commands.clean_content(escape_markdown=True).convert(
            ctx, str(member)
        )

        # Make sure that the targeted member for a moderation action is not
        # the bot itself, the user of the command or the owner of the server.
        if ctx.author.id == member.id:
            raise commands.BadArgument(f"You cannot {ctx.command} yourself.")
        elif member.id == ctx.bot.user.id:
            raise commands.BadArgument(f"I'm afraid, I cannot {ctx.command} myself.")
        elif is_kerkermeister(member):
            raise commands.BadArgument(f"You cannot {ctx.command} a staff member.")
        elif member == ctx.guild.owner:
            raise commands.BadArgument(f"We won't {ctx.command} the server owner.")

        # Check if the bot has the necessary permissions to execute the command
        # and make sure that the role hierarchy does not forbid the action.
        if member.top_role >= ctx.me.top_role:
            if ctx.author != ctx.guild.owner and member.top_role >= ctx.author.top_role:
                _extra = "the two of us"
            else:
                _extra = "me"

            raise commands.BadArgument(
                f"{safe_name} has equal or higher privileges than {_extra}."
            )
        elif member.top_role >= ctx.author.top_role:
            raise commands.BadArgument(
                f"{safe_name} has equal or higher privileges than you."
            )

        return member


class Moderation(commands.Cog):
    def __init__(self, bot: SquadBot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self, ctx: commands.Context, target: CheckedMember, *, reason: str = ""
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
        self, ctx: commands.Context, target: CheckedMember, *, reason: str = ""
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

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def hackban(self, ctx: commands.Context, target_id: int, *, reason: str = ""):
        """Bans a user through their ID without messaging them.

        This command is intended to be used on users who are no members of the guild.
        """
        try:
            target = await CheckedMember().convert(ctx, str(target_id))
        except commands.MemberNotFound:
            target = discord.Object(target_id)

        await ctx.guild.ban(
            target,
            reason=f"By {ctx.author} for {reason or 'no reason'}",
            delete_message_days=0,
        )
        await ctx.send(f"⛔ {target_id}")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, target_id: int, *, reason: str = ""):
        """Unbans a user through their ID."""
        target = discord.Object(target_id)

        await ctx.guild.unban(
            target, reason=f"By {ctx.author} for {reason or 'no reason'}"
        )
        await ctx.send(f"✅ {target_id}")


def setup(bot: SquadBot):
    bot.add_cog(Moderation(bot))
