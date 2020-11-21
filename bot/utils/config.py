from typing import Set

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    discord_auth_key: str = Field(..., env="DISCORD_TOKEN")
    discord_prefixes: Set[str] = Field(["!"], env="DISCORD_PREFIXES")
    postgres_user: str = Field(None, env="POSTGRES_USER")
    postgres_password: str = Field(None, env="POSTGRES_PASSWORD")
    postgres_db: str = Field(None, env="POSTGRES_DB")
    postgres_host: str = Field(None, env="POSTGRES_HOST")
    postgres_port: str = Field(None, env="POSTGRES_PORT")
    postgres_db_url: str = Field(None, env="POSTGRES_DB_URL")


config = Config()


def construct_database_url() -> str:
    if url := config.postgres_db_url:
        return url
    else:
        return "postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}".format(
            config.postgres_user,
            config.postgres_password,
            config.postgres_host,
            config.postgres_port,
            config.postgres_db,
        )
