"""Parse currency rows from alanchand.com HTML."""

from __future__ import annotations

import re
import logging
from typing import Any

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

_TREND_MAP = {
    "up": "up",
    "down": "down",
    "no_change": "no_change",
}


def _clean(text: str) -> str:
    """Strip whitespace and collapse inner spaces."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_trend(tag: Tag) -> str:
    """Read the CSS class of the priceSymbol span to determine trend."""
    span = tag.select_one("span.priceSymbol")
    if not span:
        return "no_change"
    classes = span.get("class", [])
    for cls in classes:
        if cls in _TREND_MAP:
            return _TREND_MAP[cls]
    return "no_change"


def parse_currencies(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Return a list of currency dicts extracted from all CurrencyTbl tables."""
    currencies: list[dict[str, Any]] = []

    for table in soup.select("table.CurrencyTbl"):
        for row in table.select("tbody tr"):
            try:
                name_el = row.select_one("td.currName")
                buy_el = row.select_one("td.buyPrice")
                sell_el = row.select_one("td.sellPrice")
                rate_el = row.select_one("td.usdRate")

                if not (name_el and buy_el and sell_el):
                    continue

                name = _clean(name_el.get_text())
                buy = _clean(buy_el.get_text())
                sell = _clean(sell_el.get_text())
                rate = _clean(rate_el.get_text()) if rate_el else "-"
                trend = _extract_trend(sell_el)

                currencies.append({
                    "name": name,
                    "buy_price": buy,
                    "sell_price": sell,
                    "usd_rate": rate,
                    "trend": trend,
                })
            except Exception:
                logger.warning("Skipping malformed currency row", exc_info=True)

    logger.info("Parsed %d currencies", len(currencies))
    return currencies
