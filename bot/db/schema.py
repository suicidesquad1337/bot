import enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB

from .connection import DATABASE as db


class Server(db.Model):
    __tablename__ = "servers"
    id: int = db.Column(db.BigInteger, primary_key=True)
    owner: int = db.Column(db.BigInteger, db.ForeignKey("owners.id"))


class ServerProperty(db.Model):
    __tablename__ = "server_properties"
    id: int = db.Column(db.BigInteger, db.ForeignKey("servers.id"), primary_key=True)
    banned_emojis_raw: [str] = db.Column(ARRAY(db.Unicode), nullable=True)
    banned_emojis_categories: [str] = db.Column(ARRAY(db.Unicode), nullable=True)
    banned_custom_emotes: [str] = db.Column(ARRAY(db.Unicode), nullable=True)
    banned_emojis_ignored_channels: [int] = db.Column(
        ARRAY(db.BigInteger), nullable=True
    )
    smaland_channel_id: int = db.Column(db.BigInteger, nullable=False)
    smaland_max_autistenpunkte: int = db.Column(db.BigInteger, nullable=False)


class GithubIntegration(db.Model):
    __tablename__ = "github_integration"
    org_name: str = db.Column(db.String, primary_key=True)
    org_id: int = db.Column(db.BigInteger, unique=True)
    properties: dict = db.Column(JSONB, nullable=False, server_default="{}")


class GithubProject(db.Model):
    __tablename__ = "github_projects"
    id: int = db.Column(db.BigInteger, primary_key=True)
    org_id: int = db.Column(db.BigInteger, db.ForeignKey("github_integration.org_id"))


class Owner(db.Model):
    __tablename__ = "owners"
    id: int = db.Column(db.BigInteger, primary_key=True)
    registered: datetime = db.Column(db.DateTime, nullable=False)
    oauth_token_discord: str = db.Column(db.String, nullable=False)


class AutistenpunkteReason(enum.Enum):
    # TODO: add more reasons
    emoji_abuse = 1
    spam = 2


class Autistenpunkt(db.Model):
    __tablename__ = "autistenpunkte"
    id: int = db.Column(db.BigInteger, primary_key=True)
    member_id: int = db.Column(db.BigInteger, nullable=False)
    server_id: int = db.Column(db.BigInteger, db.ForeignKey("servers.id"))
    score: int = db.Column(db.Integer, nullable=False)
    valid_after: datetime = db.Column(db.DateTime, nullable=False)
    valid_until: datetime = db.Column(db.DateTime, nullable=False)
    reason: str = db.Column(db.Unicode, nullable=True)
    reason_id: AutistenpunkteReason = db.Column(
        ENUM(AutistenpunkteReason), nullable=True
    )


# used for discord oauth and github name verification
class User(db.Model):
    __tablename__ = "users"
    id: int = db.Column(db.BigInteger, primary_key=True)
    discord_oauth_token: str = db.Column(db.String, nullable=False)
    github_user_id: int = db.Column(db.BigInteger, nullable=True)
