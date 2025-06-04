import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
import sentry_sdk
from fastapi import FastAPI, HTTPException as FastAPIHTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette.middleware.cors import CORSMiddleware

from app.api import register_routers  # make sure this exists
from app.config import app_configs, settings  # make sure this exists
from app.enums import ErrorCodeEnum  # make sure this exists
from app.exceptions import GenericHTTPException  # make sure this exists

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    try:
        FastAPICache.init(InMemoryBackend())

        _app.state.db_pool = await asyncpg.create_pool(
            dsn=str(settings.DATABASE_URL),
            max_size=settings.DATABASE_POOL_SIZE,
            max_inactive_connection_lifetime=settings.DATABASE_POOL_TTL,
            server_settings={"application_name": "YnterX API"},
            command_timeout=60,
        )

        log.info("Application is starting up...")
        yield
    except Exception:
        log.error("Error during application startup", exc_info=True)
    finally:
        log.info("Application is shutting down...")
        if hasattr(_app.state, "db_pool"):
            await _app.state.db_pool.close()


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

if settings.ENVIRONMENT.is_deployed:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
    )

register_routers(app)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(GenericHTTPException)
async def custom_http_exception_handler(request: Request, exc: GenericHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=exc.to_dict(),
    )


@app.exception_handler(FastAPIHTTPException)
async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
    log.error("FastAPI HTTP exception occurred", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error_code": ErrorCodeEnum.UNDEFINED.value,
            "message": exc.detail,
            "success": False,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error("Unhandled exception occurred", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": ErrorCodeEnum.INTERNAL_SERVER_ERROR.value,
            "message": "An unexpected error occurred",
            "success": False,
        },
    )


# Entry point for Docker
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
