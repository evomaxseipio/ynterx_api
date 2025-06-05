import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette.middleware.cors import CORSMiddleware

from app.api import register_routers
from app.config import app_configs, settings
from app.enums import ErrorCodeEnum
from app.exceptions import GenericHTTPException

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """
    Lifespan event handler for the FastAPI application.
    This function is used to manage startup and shutdown events for the application.
    It can be used to initialize resources like database connections or external services.
    """
    # Initialize resources here, e.g., database connections
    try:
        FastAPICache.init(InMemoryBackend())

        _app.state.db_pool = await asyncpg.create_pool(
            dsn=str(settings.DATABASE_URL),
            max_size=settings.DATABASE_POOL_SIZE,
            max_inactive_connection_lifetime=settings.DATABASE_POOL_TTL,
            server_settings={"application_name": "GCapital API"},
            command_timeout=60,  # Set a command timeout for database operations
            min_size=10,  # Mantener al menos 10 conexiones vivas
            max_queries=50000,  # Reciclar conexiones después de 50k queries
        )

        # Configurar auto-login para desarrollo local
        if settings.ENVIRONMENT.is_debug:
            from app.auth.local_dev import setup_local_dev_auth
            await setup_local_dev_auth()
            log.info("Local development auto-login configured")

        log.info("Application is starting up...")
        # Startup
        yield
        # Shutdown
    except Exception:
        log.error("Error during application startup", exc_info=True)
    finally:
        if hasattr(_app.state, "db_pool"):
            try:
                # Establecer un timeout de 10 segundos para el cierre del pool
                await asyncio.wait_for(_app.state.db_pool.close(), timeout=10.0)
            except TimeoutError:
                log.error("Timeout while closing database pool")
            except Exception as e:
                log.error(f"Error closing database pool: {e}", exc_info=True)
        log.info("Application is shutting down...")


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
