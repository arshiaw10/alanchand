"""Parse cryptocurrency cards from alanchand.com HTML."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from pricebot.models import TREND_FLAT, CryptoItem
from pricebot.scraper._html import clean, extract_trend

logger = logging.getLogger(__name__)


def parse_crypto(soup: BeautifulSoup) -> list[CryptoItem]:
    """Extract crypto items from the ``section.cryptoPrice`` cards."""
    items: list[CryptoItem] = []

    section = soup.select_one("section.cryptoPrice")
    if section is None:
        logger.warning("cryptoPrice section not found")
        return items

    for card in section.select("div.card.shadow"):
        name_el = card.select_one("h3 a")
        if not name_el:
            continue
        symbol_el = card.select_one("span.text-secondary")

        # Two price spans: fw-bold = Toman price, fw-normal = USD price.
        toman_price = toman_trend = usd_price = usd_trend = ""
        for span in card.select("span.fw-bold, span.fw-normal"):
            text = clean(span.get_text())
            trend = extract_trend(span)
            classes: list[str] = list(span.get("class") or [])
            if "fw-bold" in classes and not toman_price:
                toman_price, toman_trend = text, trend
            elif "fw-normal" in classes and not usd_price:
                usd_price, usd_trend = text, trend

        items.append(
            CryptoItem(
                name=clean(name_el.get_text()),
                symbol=clean(symbol_el.get_text()) if symbol_el else "",
                price_toman=toman_price,
                price_usd=usd_price,
                trend=toman_trend or usd_trend or TREND_FLAT,
            )
        )

    logger.info("Parsed %d crypto items", len(items))
    return items
