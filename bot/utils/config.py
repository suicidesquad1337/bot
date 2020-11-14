import os
from typing import List

from dotenv import load_dotenv


def load_config(root):
    load_dotenv(root / ".env")


def get_prefixes() -> List[str]:
    return os.getenv("DISCORD_PREFIXES").split(",")


def get_token() -> str:
    return os.getenv("DISCORD_TOKEN")


def get_database_url() -> str:
    return os.getenv("DATABASE_URL")
