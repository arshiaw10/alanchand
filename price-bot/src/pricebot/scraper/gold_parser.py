"""Parse gold & coin cards from alanchand.com HTML."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from pricebot.models import GoldItem
from pricebot.scraper._html import clean, extract_trend

logger = logging.getLogger(__name__)


def parse_gold(soup: BeautifulSoup) -> list[GoldItem]:
    """Extract gold/coin items from ``div.goldCard`` elements."""
    items: list[GoldItem] = []

    for card in soup.select("div.goldCard"):
        name_el = card.select_one("h3 a")
        price_el = card.select_one("span.priceSymbol")
        if not (name_el and price_el):
            continue

        items.append(
            GoldItem(
                name=clean(name_el.get_text()),
                price=clean(price_el.get_text()),
                trend=extract_trend(price_el),
            )
        )

    logger.info("Parsed %d gold/coin items", len(items))
    return items
