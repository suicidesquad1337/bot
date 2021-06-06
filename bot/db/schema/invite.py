from sqlalchemy.dialects.postgresql import insert

from .. import DATABASE as db


class InvitedMember(db.Model):
    __tablename__ = "invited_members"
    member_id: int = db.Column(db.BigInteger(), primary_key=True)
    inviter: int = db.Column(db.BigInteger(), nullable=False)
    invite: str = db.Column(db.String(), nullable=True)

    # Set the inviter of a user or update them
    @staticmethod
    async def set_inviter_or_update(
        member_id: int, inviter_id: int, invite: str = None
    ):
        inviter_insert = insert(InvitedMember).values(
            member_id=member_id, inviter=inviter_id, invite=invite
        )
        inviter_insert = inviter_insert.on_conflict_do_update(
            index_elements=[InvitedMember.member_id],
            set_=dict(member_id=member_id, inviter=inviter_id, invite=invite),
        )
        await inviter_insert.gino.model(InvitedMember).first()
