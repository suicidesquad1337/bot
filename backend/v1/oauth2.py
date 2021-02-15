import logging

from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from bot.db.schema import OAuth2DiscordEntry
from bot.utils.config import BOT_CONFIG

logger = logging.getLogger(__name__)
router = APIRouter()


oauth = OAuth()

oauth.register(
    name="discord",
    client_id=BOT_CONFIG.discord_client_id,
    client_secret=BOT_CONFIG.discord_client_secret,
    access_token_url=BOT_CONFIG.discord_access_token_url,
    access_token_params=BOT_CONFIG.discord_access_token_params,
    authorize_url=BOT_CONFIG.discord_authorize_url,
    authorize_params=BOT_CONFIG.discord_authorize_params,
    api_base_url=BOT_CONFIG.discord_api_base_url,
    client_kwargs=BOT_CONFIG.discord_client_kwargs,
)


@router.get("/callback", status_code=status.HTTP_302_FOUND)
async def oauth2_callback(request: Request):
    try:
        token: OAuth2Token = await oauth.discord.authorize_access_token(request)
        # check if the token has all required scopes from the bot config
        # and redirect to login page if not.
        if not all(
            e in token["scope"].split(" ")
            for e in BOT_CONFIG.discord_client_kwargs["scope"].split(" ")
        ):
            return RedirectResponse(url=request.url_for("prepare_oauth2"))

        # get the userinfo to get the user id to store the token with the user id in
        # the database
        userinfo = (
            await oauth.discord.get(
                BOT_CONFIG.discord_api_base_url + "users/@me", token=token
            )
        ).json()

        # save the token in the database
        await OAuth2DiscordEntry.insert_or_update(
            user_id=int(userinfo["id"]),
            token=token,
        )
        # redirect the user to the oauth2 successful page.
        return RedirectResponse(
            url=BOT_CONFIG.backend_redirect_url_after_successful_oauth2
        )

    except OAuthError as error:
        # send error message to the user
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error.description
        )


# prepare the oauth2 login: generate scopes, create state etc pp.
@router.get("/login")
async def prepare_oauth2(request: Request):
    return await oauth.discord.authorize_redirect(
        request, request.url_for("oauth2_callback")
    )
