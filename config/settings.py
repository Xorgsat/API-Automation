"""Configuration management module.

Provides strongly-typed configuration loaded from YAML environment profiles
with environment variable overrides and safe secret masking.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class AuthSettings(BaseModel):
    """Authentication credential configuration."""

    username: str = Field(default="admin", description="API admin username")
    password: str = Field(default="password123", description="API admin password")


class LoggingSettings(BaseModel):
    """Logging and diagnostics configuration."""

    level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")
    mask_secrets: bool = Field(default=True, description="Whether to mask tokens and passwords")


class Settings(BaseModel):
    """Global test framework configuration."""

    environment: str = Field(default="dev", description="Target environment name")
    base_url: str = Field(
        default="https://restful-booker.herokuapp.com",
        description="Base URL of target API",
    )
    timeout: float = Field(default=15.0, description="Default HTTP request timeout in seconds")
    max_retries: int = Field(default=2, description="Max retry attempts for idempotent operations")
    retry_backoff: float = Field(
        default=0.5, description="Initial backoff multiplier between retries"
    )
    auth: AuthSettings = Field(default_factory=AuthSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    @classmethod
    def load(cls, env_name: str | None = None) -> Settings:
        """Load configuration from YAML file matching the environment, with env var overrides."""
        env = env_name or os.getenv("API_ENV", "dev").lower()
        root_dir = Path(__file__).resolve().parent.parent
        env_file = root_dir / "config" / "environments" / f"{env}.yaml"

        data: dict[str, Any] = {}
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    data = loaded

        # Apply environment variable overrides if present
        if base_url := os.getenv("API_BASE_URL"):
            data["base_url"] = base_url
        if timeout := os.getenv("API_TIMEOUT"):
            data["timeout"] = float(timeout)
        if max_retries := os.getenv("API_MAX_RETRIES"):
            data["max_retries"] = int(max_retries)
        if retry_backoff := os.getenv("API_RETRY_BACKOFF"):
            data["retry_backoff"] = float(retry_backoff)

        # Auth overrides
        auth_data = data.get("auth", {})
        if auth_user := os.getenv("API_AUTH_USERNAME"):
            auth_data["username"] = auth_user
        if auth_pass := os.getenv("API_AUTH_PASSWORD"):
            auth_data["password"] = auth_pass
        if auth_data:
            data["auth"] = auth_data

        # Logging overrides
        log_data = data.get("logging", {})
        if log_level := os.getenv("API_LOG_LEVEL"):
            log_data["level"] = log_level
        if mask_secrets := os.getenv("API_MASK_SECRETS"):
            log_data["mask_secrets"] = mask_secrets.lower() in ("true", "1", "yes")
        if log_data:
            data["logging"] = log_data

        data["environment"] = env
        return cls(**data)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings."""
    return Settings.load()
