import discord
from sqlalchemy.dialects.postgresql import insert

from .. import DATABASE as db


class Autistenpunkte(db.Model):
    __tablename__ = "autistenpunkte"

    user_id = db.Column(db.BigInteger(), primary_key=True)
    score = db.Column(db.Integer())

    @staticmethod
    async def insert_or_increase_score(user: discord.User, score: int):
        # Build a query that either inserts the score if no column for the user
        # exists yet or increases the score a user already has by the given value.
        user_insert = insert(Autistenpunkte).values(user_id=user.id, score=score)
        user_insert = user_insert.on_conflict_do_update(
            index_elements=[Autistenpunkte.user_id],
            set_=dict(score=Autistenpunkte.score + score),
        )

        await user_insert.gino.model(Autistenpunkte).first()
