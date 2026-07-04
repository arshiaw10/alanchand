"""Main scraper – downloads the homepage and delegates to sub-parsers."""

from __future__ import annotations

import re
import logging
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

from config import Config
from scraper.currency_parser import parse_currencies
from scraper.gold_parser import parse_gold
from scraper.crypto_parser import parse_crypto

logger = logging.getLogger(__name__)


def _extract_update_time(soup: BeautifulSoup) -> str:
    """Pull the 'آخرین بروز رسانی' timestamp shown on the page."""
    p = soup.select_one("section.container-sm p.text-center")
    if p:
        raw = p.get_text(strip=True)
        # Strip the label prefix
        cleaned = re.sub(r"^آخرین بروز رسانی\s*:\s*", "", raw)
        return cleaned
    return ""


def scrape_all() -> dict[str, Any]:
    """Fetch the homepage, parse every section, return a normalised dict."""
    headers = {"User-Agent": Config.USER_AGENT}
    resp = requests.get(
        Config.SOURCE_URL,
        headers=headers,
        timeout=Config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    now_iso = datetime.now(timezone.utc).isoformat()
    website_time = _extract_update_time(soup)

    data: dict[str, Any] = {
        "updated_at": website_time,
        "scraped_at": now_iso,
        "currencies": parse_currencies(soup),
        "gold": parse_gold(soup),
        "crypto": parse_crypto(soup),
    }

    logger.info(
        "Scrape complete: %d currencies, %d gold, %d crypto",
        len(data["currencies"]),
        len(data["gold"]),
        len(data["crypto"]),
    )
    return data
