"""Background scheduler that triggers periodic scrapes."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from pricebot.config import ScraperConfig
from pricebot.services.market_service import MarketService

logger = logging.getLogger(__name__)

JOB_ID = "market_scrape"


class TaskScheduler:
    """Owns the APScheduler instance and the single scrape job."""

    def __init__(self, service: MarketService, config: ScraperConfig) -> None:
        self._service = service
        self._config = config
        self._scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        """Register the periodic scrape job and start the scheduler."""
        self._scheduler.add_job(
            self._run_scrape,
            trigger=IntervalTrigger(minutes=self._config.interval_minutes),
            id=JOB_ID,
            name="Scrape market data",
            replace_existing=True,
            next_run_time=datetime.now(UTC) + timedelta(seconds=5),
        )
        self._scheduler.start()
        logger.info("Scheduler started – scraping every %d min", self._config.interval_minutes)

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    def _run_scrape(self) -> None:
        try:
            if self._service.run_scrape():
                job = self._scheduler.get_job(JOB_ID)
                if job and job.next_run_time:
                    self._service.set_next_run(job.next_run_time)
        except Exception:
            logger.exception("Unhandled error in scrape job")
