"""Application configuration using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object for the AURA backend foundation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="AURA Backend", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ALLOWED_ORIGINS",
    )

    postgres_url: str = Field(
        default="postgresql+psycopg://aura:aura@localhost:5432/aura",
        alias="POSTGRES_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    jwt_secret_key: str = Field(default="change-me-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    ai_server_url: str = Field(default="http://localhost:8001", alias="AI_SERVER_URL")
    ai_server_model: str = Field(default="Qwen3.5-4B", alias="AI_SERVER_MODEL")
    internal_api_token: str = Field(default="", alias="INTERNAL_API_TOKEN")
    storage_server_url: str = Field(default="http://localhost:9000", alias="STORAGE_SERVER_URL")

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any, info: ValidationInfo) -> list[str]:
        """Normalize CORS origins from environment values."""
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance for the application."""
    return Settings()
