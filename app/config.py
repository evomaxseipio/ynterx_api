from typing import Any, ClassVar

from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import Environment


class CustomBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class Config(CustomBaseSettings):
    DATABASE_URL: PostgresDsn
    DATABASE_ASYNC_URL: PostgresDsn
    DB_POOL_MIN_SIZE: int = 10
    DB_POOL_MAX_SIZE: int = 10
    DATABASE_POOL_SIZE: int = 16
    DATABASE_POOL_TTL: int = 60 * 20  # 20 minutes
    DATABASE_POOL_PRE_PING: bool = True

    ENVIRONMENT: Environment = Environment.PRODUCTION

    SENTRY_DSN: str | None = None

    CORS_ORIGINS: list[str] = ["*"]
    # CORS_ORIGINS_REGEX: str | None = None
    CORS_ORIGINS_REGEX: ClassVar[str] = r"^https?://localhost(:\\d+)?$"

    CORS_HEADERS: list[str] = ["*"]

    APP_VERSION: str = "0.1"

    CACHE_EXPIRE_SECONDS: int = 60 * 60 * 24  # 24 hours
    AUTH_SESSION_TTL_SECONDS: int = 60 * 10  # 10 minutes

    # SMTP Configuration
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_TLS: bool = True

    USE_GOOGLE_DRIVE: bool = False

    @model_validator(mode="after")
    def validate_sentry_non_local(self) -> "Config":
        if self.ENVIRONMENT.is_deployed and not self.SENTRY_DSN:
            raise ValueError("Sentry is not set")

        return self


settings = Config()  # type: ignore

app_configs: dict[str, Any] = {"title": "ynterxal API", "version": settings.APP_VERSION}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs
