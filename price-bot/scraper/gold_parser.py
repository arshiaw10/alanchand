"""Parse gold & coin cards from alanchand.com HTML."""

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
    return re.sub(r"\s+", " ", text).strip()


def _extract_trend(span: Tag) -> str:
    classes = span.get("class", [])
    for cls in classes:
        if cls in _TREND_MAP:
            return _TREND_MAP[cls]
    return "no_change"


def parse_gold(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Return a list of gold/coin dicts from goldCard elements."""
    items: list[dict[str, Any]] = []

    for card in soup.select("div.goldCard"):
        try:
            name_el = card.select_one("h3 a")
            price_el = card.select_one("span.priceSymbol")

            if not name_el or not price_el:
                continue

            name = _clean(name_el.get_text())
            price_text = _clean(price_el.get_text())
            trend = _extract_trend(price_el)

            items.append({
                "name": name,
                "price": price_text,
                "trend": trend,
            })
        except Exception:
            logger.warning("Skipping malformed gold card", exc_info=True)

    logger.info("Parsed %d gold/coin items", len(items))
    return items
