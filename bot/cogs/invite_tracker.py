import asyncio
import logging
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from ..db.schema import InvitedMember
from ..squadbot import SquadBot

logger = logging.getLogger(__name__)

lock = asyncio.Lock()


class InviteTracker(commands.Cog):
    def __init__(self, bot: SquadBot):
        self.bot = bot
        self._invites: dict = {}

    async def _get_invites(self):
        for invite in await self.bot.guilds[0].invites():
            async with lock:
                self._invites[invite.id] = invite

    @commands.Cog.listener()
    async def on_ready(self):
        # when connected, get all server invites
        await self._get_invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        # add new invites to the record
        async with lock:
            self._invites[invite.id] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        # remove deleted invites from the record
        async with lock:
            self._invites.pop(invite.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Bots don't use invites, so we can't match one either.
        if member.bot:
            logger.debug(f"Bot account {member.id} joined, no actions taken")
            return

        # query the saved invites before the user joined the server (old invite count).
        try:
            async with lock:
                invite: discord.Invite = next(
                    filter(
                        lambda i: i.uses > self._invites[i.id].uses,
                        await member.guild.invites(),
                    )
                )
        except StopIteration:
            # no invite found.
            await member.kick(
                reason=f"Failed to associate an invite with user {member}!"
            )
        else:
            try:
                await invite.inviter.send(
                    f"""{member} used your invite ``{invite.id}`` to join \
{member.guild.name}. You can revoke the invite and therefore kick the \
member(s) by using the ``invite revoke`` command."""
                )
            except discord.Forbidden:
                # Inviter has disabled dms or blocked the bot
                pass
            await InvitedMember.create(
                member_id=member.id, inviter=invite.inviter.id, invite=invite.id
            )
        await self._get_invites()

    async def delete_invites(self, inviter_id: int):
        # Get (hopefully) all server invites from the discord api
        for invite in await self.bot.guilds[0].invites():
            # check if the creator of the invite equals the inviter_id
            if invite.inviter.id == inviter_id:
                try:
                    # Delete the invite
                    await invite.delete()
                except discord.NotFound:
                    # Invite is already deleted (for some reason (see issue #13)).
                    logger.warning("Failed to delete invite (maybe already deleted).")
                # Remove invite from local "cache"
                async with lock:
                    self._invites.pop(invite.id)

    # remove members invited by the inviter with ``inviter_id``
    async def remove_invited_members(self, inviter_id: int, min_age: datetime = None):
        if not min_age:
            min_age = datetime.utcnow() - timedelta(days=1)
        # climb the tree
        # This could lead to big I/O both on the database and the discord api.
        for i in await InvitedMember.query.where(
            InvitedMember.inviter == inviter_id
        ).gino.all():
            # Try to get the member
            member: discord.Member = self.bot.guilds[0].get_member(i.member_id)
            # If the user is on the server (a member), proceed
            if member:
                # Check if the user is longer than required on the server
                if member.joined_at > min_age:
                    # if less, kick him
                    await member.kick(
                        reason=f"""Inviter ({inviter_id}) left the server\
 and the user was less than the required time to be independent on the server."""
                    )
                    # ... and delete all their invites
                    await self.delete_invites(member.id)
                    # ... and further climb the tree
                    await self.remove_invited_members(i.member_id, min_age)
                    # ... and delete the relation from the database
                    await i.delete()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # a bot can still create invites. Therefore we check if the bot member
        # did create invites and apply the same rules as with normal members.
        if member.bot:
            await self.delete_invites(member.id)
            await self.remove_invited_members(member.id)
            # The bot itself is not in the database. We're done here.
            logger.debug(f"Member remove event for bot account {member.id}")
            return

        # check if the member is in the database (legacy and missed entries due to down
        # time
        if invitedMember := await InvitedMember.get(member.id):
            # Search other members connected to the current leaving member
            try:
                await self.remove_invited_members(invitedMember.member_id)
                await self.delete_invites(invitedMember.member_id)
            # delete the old member from the database
            finally:
                await invitedMember.delete()
        else:
            logging.warning(f"Failed to climb the invitation tree for {member.id}")

    @commands.guild_only()
    @commands.group(name="invite", aliases=["i"])
    async def invite(self, ctx: commands.Context):
        """Manage invites"""
        # This is only used to create a command group
        pass

    @commands.guild_only()
    @invite.command(name="revoke", aliases=["r"])
    async def revoke_invite(
        self, ctx: commands.Context, invite: discord.Invite, kick_users: bool = False
    ):
        """Revoke an invite created by you. Optionally kick all members who used it."""
        # Check if the message author actually created this invite
        if invite.inviter == ctx.author:
            # Delete the invite
            await invite.delete(reason=f"Requested by {ctx.author}.")
            if kick_users:
                # If kick_users is True, kick members who used this invite.
                await self.remove_invited_members(ctx.author.id)
                await ctx.send(f"Revoked invite {invite.id} and kicked users.")
            else:
                await ctx.send(f"Revoked invite {invite.id}.")
        else:
            # If they did not, delete the invite asap so no other user can grab it.
            await ctx.message.delete()

    @commands.guild_only()
    @invite.command(name="list", aliases=["ls", "l"])
    async def list_invites(self, ctx: commands.Context):
        invites: [discord.Invite] = []
        """Let the bot send you a DM with all your known invites."""
        for invite in await ctx.guild.invites():
            # Loop over all invites and check if the invite creator is the message
            # author and if so add them to the list
            if invite.inviter == ctx.author:
                invites.append(invite)
        invites_msg = ""
        for invite in invites:
            # Format the message ``<invite> ``
            invites_msg += f"{invite.id} "
        try:
            # Send the author a DM with they invites so we don't leak them in the public
            await ctx.author.send(
                f"You have a total of {len(invites)} invite(s)\n{invites_msg}"
            )
        # User has disabled DMs.
        except discord.Forbidden:
            await ctx.send("Please enable DMs.")

    @commands.guild_only()
    @invite.command(name="kick", aliases=["k"])
    async def kick_member(
        self,
        ctx: commands.Context,
        member: discord.Member,
        climb_tree: bool = False,
        revoke_invite: bool = True,
        *,
        reason: str = None,
    ):
        """Kick a member you have invited."""
        if member.joined_at < (datetime.utcnow() - timedelta(days=270)):
            await ctx.send("Member is independent from you.")
            return
        # Load the member from the database
        if invitedMember := await InvitedMember.get(member.id):
            # Check if the author actually invited the member
            if invitedMember.inviter == ctx.author.id:
                # Kick 'em
                await ctx.guild.kick(
                    member,
                    reason=f"{ctx.author} revoked invite for \
                this user for {reason or 'no reason'}.",
                )
                await ctx.send(f"Kicked member {member}")
                if climb_tree:
                    # Kick all members who the member invited. Ignoring time.
                    await self.remove_invited_members(member.id, datetime.min)
                if revoke_invite:
                    for invite in await ctx.guild.invites():
                        # Delete the invite used by the member to join so they can't
                        # rejoin with the same invite.
                        if invite.id == invitedMember.invite:
                            await invite.delete()
                            break
            else:
                raise commands.BadArgument("Not invited by you!")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @invite.command(name="set", aliases=["s"])
    async def set_inviter(
        self,
        ctx: commands.Context,
        member: discord.Member,
        inviter: discord.User,
        invite: discord.Invite = None,
    ):
        """Manual set the inviter of a member (useful if the bot was offline)"""
        # Use helper method to either set the inviter or update the inviter.
        await InvitedMember.set_inviter_or_update(member.id, inviter.id, invite)
        # Send reply
        await ctx.send(f"Set {inviter} as inviter of {member}.")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @invite.command(name="by", aliases=["b", "get", "g"])
    async def get_inviter(self, ctx: commands.Context, member: discord.Member):
        """Get the inviter of a member"""
        if invitedMember := await InvitedMember.get(member.id):
            await ctx.send(
                f"{member} was invited by {self.bot.get_user(invitedMember.inviter)}."
            )
        else:
            await ctx.send(f"{member} not found.")


def setup(bot: SquadBot):
    bot.add_cog(InviteTracker(bot))
