"""Entry point – wires configuration, scraper, scheduler, and the Telegram bot."""

from __future__ import annotations

import logging
import signal
import sys

from pricebot.bot.app import build_app
from pricebot.config import ConfigError, load_config
from pricebot.scraper.scraper import MarketScraper
from pricebot.services.market_service import MarketService
from pricebot.services.scheduler import TaskScheduler
from pricebot.storage.repository import MarketDataRepository

logger = logging.getLogger(__name__)


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    setup_logging(config.log_level)
    logger.info("Starting price-bot")

    repo = MarketDataRepository(config.data_file)
    scraper = MarketScraper(config.scraper)
    service = MarketService(repository=repo, scraper=scraper)

    scheduler = TaskScheduler(service, config.scraper)
    scheduler.start()

    app = build_app(config.bot.token, service)

    def _shutdown(signum: int, _frame: object) -> None:
        logger.info("Received signal %s – shutting down", signum)
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        app.run_polling(drop_pending_updates=True)
    finally:
        scheduler.shutdown()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
