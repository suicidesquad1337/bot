import os
from typing import List


def get_prefixes() -> List[str]:
    return os.getenv("DISCORD_PREFIXES").split(",")


def get_token() -> str:
    return os.getenv("DISCORD_TOKEN")


def get_database_url() -> str:
    if url := os.getenv("POSTGRES_DB_URL"):
        return url
    else:
        return "postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}".format(
            os.getenv("POSTGRES_USER"),
            os.getenv("POSTGRES_PASSWORD"),
            os.getenv("POSTGRES_HOST"),
            os.getenv("POSTGRES_PORT"),
            os.getenv("POSTGRES_DB"),
        )
