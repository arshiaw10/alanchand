"""Entry point – wires together the scraper, scheduler, and Telegram bot."""

from __future__ import annotations

import asyncio
import logging
import sys

from config import Config
from storage.repository import MarketDataRepository
from services.market_service import MarketService
from services.scheduler import TaskScheduler
from bot.telegram_bot import build_app


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    if not Config.TELEGRAM_BOT_TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN is not set – aborting")
        sys.exit(1)

    # --- services ---
    repo = MarketDataRepository()
    service = MarketService(repo)

    # --- background scraper ---
    scheduler = TaskScheduler(service)
    scheduler.start()

    # --- telegram bot ---
    app = build_app()
    app.bot_data["market_service"] = service

    logger.info("Starting Telegram bot …")
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
        app.run_polling(drop_pending_updates=True)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
