"""Parse cryptocurrency cards from alanchand.com HTML."""

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


def parse_crypto(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Return a list of crypto dicts from the crypto section cards."""
    items: list[dict[str, Any]] = []

    # Crypto cards live inside section.cryptoPrice
    section = soup.select_one("section.cryptoPrice")
    if section is None:
        logger.warning("cryptoPrice section not found")
        return items

    for card in section.select("div.card.shadow"):
        try:
            name_el = card.select_one("h3 a")
            eng_el = card.select_one("span.text-secondary")

            if not name_el:
                continue

            name_fa = _clean(name_el.get_text())
            name_en = _clean(eng_el.get_text()) if eng_el else ""

            # Two price spans: first = Toman, second = USD
            price_spans = card.select("span.fw-bold, span.fw-normal")

            toman_price = ""
            toman_trend = "no_change"
            usd_price = ""
            usd_trend = "no_change"

            for span in price_spans:
                text = _clean(span.get_text())
                trend = _extract_trend(span)
                if "fw-bold" in (span.get("class") or []):
                    toman_price = text
                    toman_trend = trend
                elif "fw-normal" in (span.get("class") or []):
                    usd_price = text
                    usd_trend = trend

            items.append({
                "name": name_fa,
                "symbol": name_en,
                "price_toman": toman_price,
                "price_usd": usd_price,
                "trend": toman_trend,
            })
        except Exception:
            logger.warning("Skipping malformed crypto card", exc_info=True)

    logger.info("Parsed %d crypto items", len(items))
    return items
