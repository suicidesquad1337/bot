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
        self._invites: {} = {}

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
member(s) by using the ``revoke`` command."""
                )
            except discord.Forbidden:
                # Inviter has disabled dms or blocked the bot
                pass
            await InvitedMember.create(
                member_id=member.id,
                inviter=invite.inviter.id,
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
                    # Invite is already deleted (for some reason lol).
                    logger.warning("Failed to delete invite (maybe already deleted).")
                # Remove invite from local "cache"
                async with lock:
                    self._invites.pop(invite.id)

    # remove members invited by the inviter with ``inviter_id``
    async def remove_invited_members(self, inviter_id: int):
        # climb the tree
        # This could lead to big I/O both on the database and the discord api.
        for i in await InvitedMember.query.where(
            InvitedMember.inviter == inviter_id
        ).gino.all():
            # Try to get the member
            member: discord.Member = self.bot.guilds[0].get_member(i.member_id)
            # If the user is on the server (a member), proceed
            if member:
                # Check if the user is a day or longer on the server
                if member.joined_at > (datetime.utcnow() - timedelta(days=1)):
                    # if less, kick him
                    await member.kick(
                        reason=f"""Inviter ({inviter_id}) left the server\
 and the user was less than a day on the server."""
                    )
                    # ... and delete all their invites
                    await self.delete_invites(member.id)
                    # ... and further climb the tree
                    await self.remove_invited_members(i.member_id)
                    # ... and delete the relation from the database
                    await i.delete()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # get all invites from the guild
        for invite in await member.guild.invites():
            # check if the member has the invite created
            if invite.inviter == member:
                # delete the invite if the case
                await invite.delete()

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
            logging.warning(
                f"Failed to climb the invitation tree for {invitedMember.member_id}"
            )


def setup(bot: SquadBot):
    bot.add_cog(InviteTracker(bot))
