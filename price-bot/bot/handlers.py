"""Telegram bot command and callback handlers."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import main_menu, back_button, currencies_list
from services.market_service import MarketService

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "\U0001f44b به ربات قیمت بازار خوش آمدید!\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "قیمت‌های لحظه‌ای ارز، طلا و رمزارز\n"
    "از alanchand.com\n\n"
    "یکی از بخش‌های زیر را انتخاب کنید:"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start."""
    await update.message.reply_text(
        WELCOME_TEXT, reply_markup=main_menu()
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the 'Back' button – re-show the main menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(WELCOME_TEXT, reply_markup=main_menu())


async def section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback_data 'section:<key>' to the correct formatted output."""
    query = update.callback_query
    await query.answer()

    data: MarketService = context.bot_data["market_service"]
    payload = query.data  # e.g. "section:currencies"
    key = payload.split(":", 1)[1] if ":" in payload else ""

    if key == "all":
        text = data.get_full_report()
        await query.edit_message_text(text, reply_markup=back_button())
    elif key == "status":
        text = data.status_text()
        await query.edit_message_text(text, reply_markup=back_button())
    elif key == "currencies":
        names = [c["name"] for c in data.get_currencies()]
        if not names:
            await query.edit_message_text(
                "\u26a0\ufe0f داده ارزی موجود نیست.",
                reply_markup=back_button(),
            )
            return
        await query.edit_message_text(
            "\U0001f4b5 یک ارز را انتخاب کنید:",
            reply_markup=currencies_list(names),
        )
    elif key in ("gold", "crypto"):
        text = data.get_section(key)
        await query.edit_message_text(text, reply_markup=back_button())
    else:
        await query.edit_message_text("گزینه نامعتبر.", reply_markup=back_button())


async def currency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'currency:<index>' – show single currency detail."""
    query = update.callback_query
    await query.answer()

    data: MarketService = context.bot_data["market_service"]
    payload = query.data
    try:
        index = int(payload.split(":", 1)[1])
    except (ValueError, IndexError):
        await query.edit_message_text("خطا در دریافت اطلاعات.", reply_markup=back_button())
        return

    text = data.get_single_currency(index)
    if text is None:
        await query.edit_message_text("ارز مورد نظر یافت نشد.", reply_markup=back_button())
        return
    await query.edit_message_text(text, reply_markup=back_button())
