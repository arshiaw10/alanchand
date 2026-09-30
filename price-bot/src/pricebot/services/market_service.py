"""Business logic tying scraping, storage, and scheduling together."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime

from pricebot.models import MarketData, unknown_market_data
from pricebot.scraper.scraper import MarketScraper, ScrapeError
from pricebot.storage.repository import MarketDataRepository

logger = logging.getLogger(__name__)


class MarketService:
    """Facade used by bot handlers and the scheduler."""

    def __init__(
        self,
        repository: MarketDataRepository,
        scraper: MarketScraper,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._scraper = scraper
        self._clock = clock or datetime.now
        self._last_error: str | None = None
        self._next_run: datetime | None = None
        self._cache: MarketData | None = None

    # -- scraping ---------------------------------------------------------

    def run_scrape(self) -> bool:
        """Execute one scrape cycle. Returns True on success."""
        try:
            data = self._scraper.scrape()
        except ScrapeError:
            self._last_error = "scrape failed (network or parse error)"
            logger.exception("Scrape failed")
            return False
        self._repository.save(data)
        self._cache = data
        self._last_error = None
        return True

    # -- data access --------------------------------------------------------

    def snapshot(self) -> MarketData:
        """Current snapshot, cached in memory and loaded from disk on demand."""
        if self._cache is None:
            self._cache = self._repository.load() or unknown_market_data()
        return self._cache

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def set_next_run(self, when: datetime) -> None:
        self._next_run = when

    # -- presentation helpers ----------------------------------------------

    @staticmethod
    def last_scrape_text() -> str:
        return ""

    def next_run_text(self) -> str:
        if self._next_run is None:
            return ""
        return self._next_run.strftime("%H:%M UTC")

    def last_scrape_time(self) -> datetime | None:
        return self.snapshot().scraped_at_dt
