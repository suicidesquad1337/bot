import logging
from typing import Set

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    # The Discord bot prefixes for invoking commands in chat.
    discord_prefixes: Set[str] = Field(["!"], env="DISCORD_PREFIXES")

    # The Discord bot token obtained from the Discord Developer Portal.
    discord_token: str = Field(..., env="DISCORD_TOKEN")

    # The discord application id and secret used for oauth2. Can be obtained from the
    # Discord Developer Portal.
    discord_client_id: str = Field(..., env="DISCORD_CLIENT_ID")
    discord_client_secret: str = Field(..., env="DISCORD_CLIENT_SECRET")

    # Significant roles of the guild.
    kerkermeister_role_id: int = Field(..., env="KERKERMEISTER_ROLE_ID")

    # no need to change the following
    discord_access_token_url: str = Field(
        "https://discord.com/api/oauth2/token", env="DISCORD_ACCESS_TOKEN_URL"
    )
    discord_access_token_params: str = Field(None, env="DISCORD_ACCESS_TOKEN_PARAMS")
    discord_authorize_url: str = Field(
        "https://discord.com/api/oauth2/authorize", env="DISCORD_AUTHORIZE_URL"
    )
    discord_authorize_params: str = Field(None, env="DISCORD_AUTHORIZE_PARAMS")
    discord_access_token_revoke_url: str = Field(
        "https://discord.com/api/oauth2/token/revoke",
        env="DISCORD_ACCESS_TOKEN_REVOKE_URL",
    )
    discord_api_base_url: str = Field(
        "https://discord.com/api/v8/", env="DISCORD_API_BASE_URL"
    )
    discord_client_kwargs: dict = Field(
        {"scope": "connections identify"}, env="DISCORD_CLIENT_KWARGS"
    )

    # The user name, password, and database for the postgres database.
    postgres_user: str = Field(None, env="POSTGRES_USER")
    postgres_password: str = Field(None, env="POSTGRES_PASSWORD")
    postgres_db: str = Field(None, env="POSTGRES_DB")
    postgres_host: str = Field(None, env="POSTGRES_HOST")
    postgres_port: str = Field(None, env="POSTGRES_PORT")
    # If a user wishes to work with a given database URL directly to take
    # advantage of further configuration options, this can be alternatively
    # used instead of the above POSTGRES_* options.
    postgres_db_url: str = Field(None, env="POSTGRES_DB_URL")

    # The list of allowed origins. If you have a frontend which uses this api,
    # you'll have to add the address here.
    # (see https://fastapi.tiangolo.com/tutorial/cors/?h=origin#use-corsmiddleware)
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
    backend_origins_max_age: int = Field(600, env="BACKEND_ORIGINS_MAX_AGE")

    # A random string used for the state parameter in the oauth2 process.
    # You can generate one by running openssl rand -hex 32
    backend_oauth2_session_secret: str = Field(..., env="BACKEND_OAUTH2_SESSION_SECRET")

    backend_discord_oauth2_url: str = Field(
        "https://discord.com/api/oauth2/authorize", env="BACKEND_DISCORD_OAUTH2_URL"
    )

    debug_mode: bool = Field(False, env="DEBUG_MODE")

    # The url the api should redirect to after a successful oauth2 operation.
    # This is optional. If not filled out,
    # it will redirect to https://discord.com/oauth2/authorized
    backend_redirect_url_after_successful_oauth2: str = Field(
        "https://discord.com/oauth2/authorized",
        env="BACKEND_REDIRECT_URL_AFTER_SUCCESSFUL_OAUTH2",
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
