"""Build the python-telegram-bot Application."""

from __future__ import annotations

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
)

from pricebot.bot import handlers
from pricebot.services.market_service import MarketService


def build_app(token: str, service: MarketService) -> Application:
    """Construct the Application with all handlers registered and the service injected."""
    app = ApplicationBuilder().token(token).build()
    app.bot_data["market_service"] = service

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CallbackQueryHandler(handlers.currency_callback, pattern=r"^currency:"))
    app.add_handler(CallbackQueryHandler(handlers.menu_callback, pattern=r"^menu$"))
    app.add_handler(CallbackQueryHandler(handlers.section_callback, pattern=r"^section:"))
    return app
