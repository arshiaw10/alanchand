"""Scraper client – fetches the alanchand.com homepage and parses every section."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from datetime import UTC, datetime

import requests
from bs4 import BeautifulSoup

from pricebot.config import ScraperConfig
from pricebot.models import CryptoItem, Currency, GoldItem, MarketData
from pricebot.scraper.crypto_parser import parse_crypto
from pricebot.scraper.currency_parser import parse_currencies
from pricebot.scraper.gold_parser import parse_gold

logger = logging.getLogger(__name__)

_UPDATE_TIME_PREFIX_RE = re.compile(r"^آخرین بروز رسانی\s*:\s*")


class ScrapeError(Exception):
    """Raised when the website cannot be fetched or parsed."""


class MarketScraper:
    """Fetch and parse a market snapshot from the source website."""

    def __init__(
        self,
        config: ScraperConfig,
        session: requests.Session | None = None,
        fetcher: Callable[[str], str] | None = None,
    ) -> None:
        self._config = config
        self._session = session or requests.Session()
        self._fetcher = fetcher  # injection point for tests

    def scrape(self) -> MarketData:
        """Fetch the homepage and return a fully parsed snapshot."""
        html = self._fetch_html()
        soup = BeautifulSoup(html, "lxml")

        data = MarketData(
            updated_at=self._extract_update_time(soup),
            scraped_at=datetime.now(UTC).isoformat(),
            currencies=parse_currencies(soup),
            gold=parse_gold(soup),
            crypto=parse_crypto(soup),
        )
        logger.info(
            "Scrape complete: %d currencies, %d gold, %d crypto",
            len(data.currencies),
            len(data.gold),
            len(data.crypto),
        )
        return data

    def _fetch_html(self) -> str:
        if self._fetcher is not None:
            return self._fetcher(self._config.source_url)
        try:
            response = self._session.get(
                self._config.source_url,
                headers={"User-Agent": self._config.user_agent},
                timeout=self._config.request_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ScrapeError(f"Failed to fetch {self._config.source_url}: {exc}") from exc
        return response.text

    @staticmethod
    def _extract_update_time(soup: BeautifulSoup) -> str:
        """Pull the 'آخرین بروز رسانی' timestamp shown on the page."""
        paragraph = soup.select_one("section.container-sm p.text-center")
        if not paragraph:
            return ""
        raw = paragraph.get_text(strip=True)
        return _UPDATE_TIME_PREFIX_RE.sub("", raw)


__all__ = ["CryptoItem", "Currency", "GoldItem", "MarketData", "MarketScraper", "ScrapeError"]
