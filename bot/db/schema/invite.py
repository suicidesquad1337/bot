from .. import DATABASE as db


class InvitedMember(db.Model):
    __tablename__ = "invited_members"
    member_id: int = db.Column(db.BigInteger(), primary_key=True)
    inviter: int = db.Column(db.BigInteger(), nullable=False)
    invite: str = db.Column(db.String(), nullable=False)
