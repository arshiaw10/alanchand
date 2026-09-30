"""Single source of truth for the data model used across scraper, storage, and bot."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

SCHEMA_VERSION = 1

TREND_UP = "up"
TREND_DOWN = "down"
TREND_FLAT = "no_change"
VALID_TRENDS = (TREND_UP, TREND_DOWN, TREND_FLAT)


@dataclass(frozen=True)
class Currency:
    """One exchange-rate row."""

    name: str
    buy_price: str
    sell_price: str
    usd_rate: str = "-"
    trend: str = TREND_FLAT


@dataclass(frozen=True)
class GoldItem:
    """One gold or coin card."""

    name: str
    price: str
    trend: str = TREND_FLAT


@dataclass(frozen=True)
class CryptoItem:
    """One cryptocurrency card."""

    name: str
    price_toman: str
    price_usd: str
    symbol: str = ""
    trend: str = TREND_FLAT


@dataclass(frozen=True)
class MarketData:
    """A full scrape snapshot, ready for JSON round-tripping."""

    updated_at: str          # website-declared timestamp (Persian text)
    scraped_at: str          # our ISO-8601 UTC scrape time
    currencies: list[Currency] = field(default_factory=list)
    gold: list[GoldItem] = field(default_factory=list)
    crypto: list[CryptoItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = SCHEMA_VERSION
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MarketData:
        return cls(
            updated_at=str(raw.get("updated_at", "")),
            scraped_at=str(raw.get("scraped_at", "")),
            currencies=[Currency(**c) for c in raw.get("currencies", [])],
            gold=[GoldItem(**g) for g in raw.get("gold", [])],
            crypto=[CryptoItem(**c) for c in raw.get("crypto", [])],
        )

    @property
    def scraped_at_dt(self) -> datetime | None:
        """Parsed scraped_at, or None when missing/unparseable."""
        if not self.scraped_at:
            return None
        try:
            return datetime.fromisoformat(self.scraped_at)
        except ValueError:
            return None

    def is_empty(self) -> bool:
        return not (self.currencies or self.gold or self.crypto)


def unknown_market_data() -> MarketData:
    """Empty snapshot used when nothing has ever been scraped."""
    return MarketData(updated_at="", scraped_at="")
