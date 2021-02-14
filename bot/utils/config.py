import logging
from typing import Set

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    discord_prefixes: Set[str] = Field(["!"], env="DISCORD_PREFIXES")
    discord_token: str = Field(..., env="DISCORD_TOKEN")

    postgres_user: str = Field(None, env="POSTGRES_USER")
    postgres_password: str = Field(None, env="POSTGRES_PASSWORD")
    postgres_db: str = Field(None, env="POSTGRES_DB")
    postgres_host: str = Field(None, env="POSTGRES_HOST")
    postgres_port: str = Field(None, env="POSTGRES_PORT")
    postgres_db_url: str = Field(None, env="POSTGRES_DB_URL")

    backend_origins_allowed: Set[str] = Field([], env="BACKEND_ORIGINS_ALLOWED")
    backend_origins_allow_credentials: bool = Field(
        True, env="BACKEND_ORIGINS_ALLOW_CREDENTIALS"
    )
    backend_origins_allowed_methods: Set[str] = Field(
        ["*"], env="BACKEND_ORIGINS_ALLOWED_METHODS"
    )
    backend_origins_allowed_headers: Set[str] = Field(
        ["*"], env="BACKEND_ORIGINS_ALLOWED_HEADERS"
    )
    backend_origins_exposed_headers: Set[str] = Field(
        [], env="BACKEND_ORIGINS_EXPOSED_HEADERS"
    )
    backend_discord_oauth2_url: str = Field(
        "https://discord.com/api/oauth2/authorize", env="BACKEND_DISCORD_OAUTH2_URL"
    )
    backend_origins_max_age: int = Field(600, env="BACKEND_ORIGINS_MAX_AGE")
    debug_mode: bool = Field(False, env="DEBUG_MODE")

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
