import os
from dataclasses import dataclass
from typing import Optional


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None and v != "" else default


@dataclass(frozen=True)
class AppConfig:
    bind_host: str = _env_str("BIND_HOST", "0.0.0.0")
    port: int = _env_int("PORT", 8000)
    refresh_interval_seconds: int = _env_int("REFRESH_INTERVAL_SECONDS", 30)
    staleness_window_seconds: int = _env_int("STALENESS_WINDOW_SECONDS", 120)
    version: str = _env_str("APP_VERSION", "0.1.0")


def load_config() -> AppConfig:
    """Load configuration from environment with safe defaults."""
    return AppConfig()
