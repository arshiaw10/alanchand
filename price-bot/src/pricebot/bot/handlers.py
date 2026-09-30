"""Telegram command and callback handlers."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from pricebot.bot import keyboards as kb
from pricebot.bot import messages as fmt
from pricebot.services.market_service import MarketService

logger = logging.getLogger(__name__)

_SERVICE_KEY = "market_service"


def _service(context: ContextTypes.DEFAULT_TYPE) -> MarketService:
    return context.bot_data[_SERVICE_KEY]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start."""
    if update.message is None:
        return
    await update.message.reply_text(fmt.render_welcome(), reply_markup=kb.main_menu())


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the main-menu back button."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    await query.edit_message_text(fmt.render_welcome(), reply_markup=kb.main_menu())


async def section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route ``section:<key>`` callbacks to the matching view."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    service = _service(context)
    key = (query.data or "").split(":", 1)[-1]

    if key == "all":
        text = fmt.render_full_report(service.snapshot())
        markup = kb.back_to_menu()
    elif key == "status":
        text = fmt.render_status(
            service.snapshot(),
            last_scrape=service.last_scrape_text(),
            next_run=service.next_run_text(),
            last_error=service.last_error,
        )
        markup = kb.back_to_menu()
    elif key == "currencies":
        names = [c.name for c in service.snapshot().currencies]
        if not names:
            text, markup = fmt.render_no_data("ارز"), kb.back_to_menu()
        else:
            text = "\U0001f4b5 یک ارز را انتخاب کنید:"
            markup = kb.currency_list(names)
    else:  # gold / crypto / unknown
        text = fmt.render_section(service.snapshot(), key)
        markup = kb.back_to_menu()

    await query.edit_message_text(text, reply_markup=markup)


async def currency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle ``currency:<index>`` – show one currency detail card."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    service = _service(context)
    try:
        index = int((query.data or "").split(":", 1)[1])
    except (IndexError, ValueError):
        index = -1

    text = fmt.render_single_currency(service.snapshot(), index)
    if text is None:
        text = "ارز مورد نظر یافت نشد."
    await query.edit_message_text(text, reply_markup=kb.back_to_menu())
