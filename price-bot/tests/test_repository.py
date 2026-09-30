"""Tests for the JSON repository."""

from __future__ import annotations

from pathlib import Path

from pricebot.models import Currency, MarketData
from pricebot.storage.repository import MarketDataRepository


def _sample() -> MarketData:
    return MarketData(
        updated_at="۱۴۰۳/۰۴/۱۵ ۱۰:۳۰",
        scraped_at="2026-09-30T10:00:00+00:00",
        currencies=[Currency(name="دلار", buy_price="61,500", sell_price="61,700")],
    )


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    repo = MarketDataRepository(tmp_path / "data.json")
    repo.save(_sample())
    loaded = repo.load()
    assert loaded == _sample()


def test_load_missing_file_returns_none(tmp_path: Path) -> None:
    repo = MarketDataRepository(tmp_path / "missing.json")
    assert repo.load() is None


def test_load_corrupted_file_returns_none_and_deletes(tmp_path: Path) -> None:
    path = tmp_path / "corrupt.json"
    path.write_text("{not valid json", encoding="utf-8")
    repo = MarketDataRepository(path)
    assert repo.load() is None
    assert not path.exists()


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    repo = MarketDataRepository(tmp_path / "a" / "b" / "data.json")
    repo.save(_sample())
    assert repo.load() is not None
