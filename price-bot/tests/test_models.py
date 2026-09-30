"""Tests for the data models."""

from __future__ import annotations

from pricebot.models import CryptoItem, Currency, GoldItem, MarketData, unknown_market_data


def test_round_trip() -> None:
    data = MarketData(
        updated_at="۱۴۰۳/۰۴/۱۵",
        scraped_at="2026-09-30T10:00:00+00:00",
        currencies=[Currency(name="دلار", buy_price="1", sell_price="2", usd_rate="1")],
        gold=[GoldItem(name="سکه", price="100")],
        crypto=[CryptoItem(name="بیت‌کوین", price_toman="3", price_usd="4", symbol="BTC")],
    )
    restored = MarketData.from_dict(data.to_dict())
    assert restored == data


def test_from_dict_with_missing_fields() -> None:
    data = MarketData.from_dict({})
    assert data.updated_at == ""
    assert data.currencies == []
    assert data.is_empty()


def test_unknown_market_data_is_empty() -> None:
    assert unknown_market_data().is_empty()


def test_scraped_at_dt() -> None:
    data = MarketData(updated_at="", scraped_at="2026-09-30T10:00:00+00:00")
    assert data.scraped_at_dt is not None
    empty = MarketData(updated_at="", scraped_at="")
    assert empty.scraped_at_dt is None
