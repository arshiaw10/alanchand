"""APScheduler wrapper – runs the scrape job in the background."""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import Config
from services.market_service import MarketService

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Thin wrapper that owns the APScheduler instance."""

    def __init__(self, service: MarketService) -> None:
        self._service = service
        self._scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        """Register the periodic scrape job and start the scheduler."""
        self._scheduler.add_job(
            self._run_scrape,
            trigger=IntervalTrigger(minutes=Config.SCRAPE_INTERVAL_MINUTES),
            id="market_scrape",
            name="Scrape alanchand.com",
            replace_existing=True,
            next_run_time=datetime.now(timezone.utc) + timedelta(seconds=5),
        )
        self._scheduler.start()
        logger.info(
            "Scheduler started – scraping every %d min", Config.SCRAPE_INTERVAL_MINUTES
        )

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    def _run_scrape(self) -> None:
        try:
            success = self._service.run_scrape()
            if success:
                # Record the next scheduled fire time
                job = self._scheduler.get_job("market_scrape")
                if job and job.next_run_time:
                    self._service.set_next_run(job.next_run_time)
        except Exception:
            logger.exception("Unhandled error in scrape job")
