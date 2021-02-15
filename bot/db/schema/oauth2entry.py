from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from sqlalchemy.dialects.postgresql import insert

from .. import DATABASE as db


class OAuth2DiscordEntry(db.Model):
    __tablename__ = "oauth2_discord_entries"
    user_id: int = db.Column(db.BigInteger(), primary_key=True)
    token_type: str = db.Column(db.String(), nullable=False)
    access_token: str = db.Column(db.String(), nullable=False)
    refresh_token: str = db.Column(db.String(), nullable=False)
    expires_at: int = db.Column(db.BigInteger(), nullable=False)
    scope: str = db.Column(db.String(), nullable=False)

    def to_token(self) -> dict:
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

    # Insert user if not exists. If the user is already in the database, update the
    # token
    @staticmethod
    async def insert_or_update(user_id: int, token: OAuth2Token):
        entry_insert = insert(OAuth2DiscordEntry).values(
            user_id=user_id,
            token_type=token["token_type"],
            access_token=token["access_token"],
            refresh_token=token["refresh_token"],
            expires_at=token["expires_at"],
            scope=token["scope"],
        )
        entry_insert = entry_insert.on_conflict_do_update(
            index_elements=[OAuth2DiscordEntry.user_id],
            set_=dict(
                token_type=token["token_type"],
                access_token=token["access_token"],
                refresh_token=token["refresh_token"],
                expires_at=token["expires_at"],
                scope=token["scope"],
            ),
        )
        await entry_insert.gino.model(OAuth2DiscordEntry).first()
