from typing import Set

import emojis
from emojis import db as emojis_db
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    discord_token: str = Field(..., env="DISCORD_TOKEN")
    discord_prefixes: Set[str] = Field(["!"], env="DISCORD_PREFIXES")
    postgres_user: str = Field(None, env="POSTGRES_USER")
    postgres_password: str = Field(None, env="POSTGRES_PASSWORD")
    postgres_db: str = Field(None, env="POSTGRES_DB")
    postgres_host: str = Field(None, env="POSTGRES_HOST")
    postgres_port: str = Field(None, env="POSTGRES_PORT")
    postgres_db_url: str = Field(None, env="POSTGRES_DB_URL")
    smaland_channel_id: int = Field(..., env="SMALAND_CHANNEL_ID")
    smaland_max_autistenpunkte: int = Field(..., env="SMALAND_MAX_AUTISTENPUNKTE")
    smaland_autistenpunkte_reset_interval: int = Field(
        3600, env="SMALAND_AUTISTENPUNKTE_RESET_INTERVAL"
    )
    smaland_autistenpunkte_ignored_channels: Set[int] = Field(
        [], env="SMALAND_AUTISTENPUNKTE_IGNORED_CHANNELS"
    )
    smaland_banned_custom_emotes: Set[str] = Field(
        [], env="SMALAND_BANNED_CUSTOM_EMOTES"
    )
    smaland_banned_emojis_raw: Set[str] = Field([], env="SMALAND_BANNED_EMOJIS_RAW")
    smaland_banned_emojis: Set[str] = Field([], env="SMALAND_BANNED_EMOJIS")
    smaland_banned_categories: Set[str] = Field(
        [], env="SMALAND_BANNED_EMOJI_CATEGORIES"
    )
    smaland_banned_tags: Set[str] = Field([], env="SMALAND_BANNED_EMOJI_TAGS")

    def construct_database_url(self) -> str:
        if url := self.postgres_db_url:
            return url
        else:
            return "postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}".format(
                self.postgres_user,
                self.postgres_password,
                self.postgres_host,
                self.postgres_port,
                self.postgres_db,
            )

    def sum_banned_emojis(self) -> Set[str]:
        banned_emojis: Set[str] = self.smaland_banned_emojis_raw

        for e in self.smaland_banned_emojis:
            banned_emojis.add(emojis.encode(e))
        for c in self.smaland_banned_categories:
            for e in emojis_db.get_emojis_by_category(c):
                banned_emojis.add(e[1])
        for t in self.smaland_banned_tags:
            for e in emojis_db.get_emojis_by_tag(t):
                banned_emojis.add(e[1])
        return banned_emojis


BOT_CONFIG = Config()
