from typing import Set

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


BOT_CONFIG = Config()
