from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bot.db import connection
from bot.utils.config import BOT_CONFIG

app = FastAPI(
    title="Squadbot",
    description="The bot of vales suicide squad.",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=BOT_CONFIG.backend_origins_allowed,
    allow_credentials=BOT_CONFIG.backend_origins_allow_credentials,
    allow_methods=BOT_CONFIG.backend_origins_allowed_methods,
    allow_headers=BOT_CONFIG.backend_origins_allowed_headers,
    expose_headers=BOT_CONFIG.backend_origins_exposed_headers,
    max_age=BOT_CONFIG.backend_origins_max_age,
)


@app.on_event("startup")
async def startup_event():
    await connection.init_connection()


@app.on_event("shutdown")
async def shutdown_event():
    await connection.close_connection()
