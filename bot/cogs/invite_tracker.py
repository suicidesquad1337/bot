from datetime import datetime, timedelta

import discord
from discord.ext import commands

from ..db.schema import InvitedMember
from ..squadbot import SquadBot


class InviteTracker(commands.Cog):
    def __init__(self, bot: SquadBot):
        self.bot = bot
        self._invites: {} = {}

    async def _get_invites(self):
        for invite in await self.bot.guilds[0].invites():
            self._invites[invite.id] = invite

    @commands.Cog.listener()
    async def on_ready(self):
        await self._get_invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        self._invites[invite.id] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        self._invites.pop(invite.id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # query the saved invites before the user joined the server (old invite count).
        try:
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
            # FIXME: Go the whole tree not only the first step
            for i in await InvitedMember.query.where(
                InvitedMember.inviter == member.id
            ).gino.all():
                # get this other member as a discord.py Member object
                other_member: discord.Member = member.guild.get_member(i.member_id)

                # Check if the member is on the server a day or longer on the server
                if other_member.joined_at > (datetime.utcnow() - timedelta(days=1)):
                    # kick 'em f this is the case
                    # FIXME: also delete the other members from the database. However
                    # FIXME: this whole thing needs to be rewritten from the first FIXME
                    await other_member.kick(
                        reason=f"""Inviter {member} left the server \
and the user was less than a day on the server."""
                    )

            # delete the old member from the database
            await invitedMember.delete()


def setup(bot: SquadBot):
    bot.add_cog(InviteTracker(bot))
