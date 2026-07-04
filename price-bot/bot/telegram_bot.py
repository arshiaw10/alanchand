"""Build and run the python-telegram-bot Application."""

from __future__ import annotations

import logging

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from config import Config
from bot.handlers import start, menu_callback, section_callback, currency_callback

logger = logging.getLogger(__name__)


def build_app() -> Application:
    """Construct the Application with all handlers registered."""
    app = (
        Application.builder()
        .token(Config.TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(currency_callback, pattern=r"^currency:"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(section_callback, pattern=r"^section:"))

    return app
