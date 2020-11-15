from .. import DATABASE as db


class Autistenpunkte(db.Model):
    __tablename__ = "autistenpunkte"

    user_id = db.Column(db.BigInteger(), primary_key=True)
    score = db.Column(db.Integer())
