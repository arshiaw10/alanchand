"""Tests for configuration loading."""

from __future__ import annotations

import pytest

from pricebot.config import ConfigError, load_config


def test_missing_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    with pytest.raises(ConfigError):
        load_config()


def test_valid_config(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("SCRAPE_INTERVAL_MINUTES", "10")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    config = load_config()
    assert config.bot.token == "123:abc"
    assert config.scraper.interval_minutes == 10
    assert config.storage.data_dir == tmp_path


def test_invalid_interval_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("SCRAPE_INTERVAL_MINUTES", "0")
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_log_level_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")
    with pytest.raises(ConfigError):
        load_config()
