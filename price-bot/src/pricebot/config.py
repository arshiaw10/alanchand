"""Typed application configuration.

All values come from environment variables (see `.env.example`).  Everything is
immutable; the objects are built once at startup and passed explicitly to the
components that need them.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# price-bot/ project root: src/pricebot/config.py -> parents[2]
BASE_DIR = Path(__file__).resolve().parents[2]

# .env lives at the project root (price-bot/.env)
load_dotenv(BASE_DIR / ".env")

DEFAULT_SOURCE_URL = "https://alanchand.com"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class ConfigError(Exception):
    """Raised when the configuration is invalid or incomplete."""


@dataclass(frozen=True)
class BotConfig:
    """Telegram bot settings."""

    token: str


@dataclass(frozen=True)
class ScraperConfig:
    """HTTP scraping settings."""

    source_url: str = DEFAULT_SOURCE_URL
    interval_minutes: int = 5
    request_timeout: int = 30
    user_agent: str = DEFAULT_USER_AGENT


@dataclass(frozen=True)
class StorageConfig:
    """Local persistence settings."""

    data_dir: Path = field(default_factory=lambda: BASE_DIR / "data")
    data_file: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_file", self.data_dir / "market_data.json")


@dataclass(frozen=True)
class AppConfig:
    """Aggregate configuration for the whole application."""

    bot: BotConfig
    scraper: ScraperConfig
    storage: StorageConfig
    log_level: str = "INFO"

    @property
    def data_file(self) -> Path:
        return self.storage.data_file


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, "")
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc


def load_config() -> AppConfig:
    """Build the configuration from the environment, validating as we go."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ConfigError(
            "TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and add your token."
        )

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if log_level not in VALID_LOG_LEVELS:
        raise ConfigError(f"LOG_LEVEL must be one of {VALID_LOG_LEVELS}, got {log_level!r}")

    scraper = ScraperConfig(
        source_url=os.getenv("SOURCE_URL", DEFAULT_SOURCE_URL),
        interval_minutes=_get_int("SCRAPE_INTERVAL_MINUTES", 5),
        request_timeout=_get_int("REQUEST_TIMEOUT", 30),
        user_agent=os.getenv("USER_AGENT", DEFAULT_USER_AGENT),
    )
    if scraper.interval_minutes < 1:
        raise ConfigError("SCRAPE_INTERVAL_MINUTES must be at least 1")
    if scraper.request_timeout < 1:
        raise ConfigError("REQUEST_TIMEOUT must be at least 1")

    storage = StorageConfig(
        data_dir=Path(os.getenv("DATA_DIR", str(BASE_DIR / "data"))),
    )

    return AppConfig(
        bot=BotConfig(token=token),
        scraper=scraper,
        storage=storage,
        log_level=log_level,
    )
