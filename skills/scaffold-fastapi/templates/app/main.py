# app/main.py

import logging
import tomllib
from contextlib import asynccontextmanager
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.logging import LoggingIntegration

from app.core.config import settings
from app.core.exception_handler import handle_generic_exception, handle_http_exception
from app.database import async_session_maker, ping_database
from app.middleware.log import setup_logger
from app.middleware.middleware import log_request, log_response
from app.routes.health import router as health_router
from app.routes.items import router as items_router

logger = setup_logger(__name__)

_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
API_VERSION: str = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))["project"][
    "version"
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with async_session_maker() as db:
            await ping_database(db)
    except Exception as exc:
        logger.error("Database connection failed: %s", exc, exc_info=True)

    yield  # Start even when DB is down at boot (soft-fail); /health/ready reports it


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    release=API_VERSION,
    traces_sample_rate=0.1,  # not env-configurable; bump here if you need more/less sampling
    integrations=[
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.WARNING,
        ),
    ],
)
app = FastAPI(
    title="__PROJECT_NAME__",
    description="__PROJECT_DESCRIPTION__",
    version=API_VERSION,
    lifespan=lifespan,
    default_response_class=JSONResponse,
)

# Middleware


@app.middleware("http")
async def request_response_logging(request: Request, call_next):
    await log_request(request)
    response = await call_next(request)
    return await log_response(request, response)


# Exception Handlers
app.add_exception_handler(Exception, handle_generic_exception)
app.add_exception_handler(HTTPException, handle_http_exception)

# CORS — "*" (default) disables allow_credentials since browsers reject that
# combination; set real origins in CORS_ORIGINS to enable credentialed requests.
_cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers last
app.include_router(health_router, tags=["Health"])
app.include_router(items_router, tags=["Items"])
