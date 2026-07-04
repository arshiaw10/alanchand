"""Telegram inline keyboards."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    """Return the primary navigation keyboard."""
    buttons = [
        [
            InlineKeyboardButton("\U0001f4b5 ارزها", callback_data="section:currencies"),
            InlineKeyboardButton("\U0001f947 طلا و سکه", callback_data="section:gold"),
        ],
        [
            InlineKeyboardButton("\u20bf رمزارز", callback_data="section:crypto"),
            InlineKeyboardButton("\U0001f30d همه بازارها", callback_data="section:all"),
        ],
        [
            InlineKeyboardButton("\u2139\ufe0f وضعیت", callback_data="section:status"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def currencies_list(names: list[str]) -> InlineKeyboardMarkup:
    """Build a keyboard with one button per currency name."""
    buttons = []
    for i, name in enumerate(names):
        buttons.append(
            [InlineKeyboardButton(name, callback_data=f"currency:{i}")]
        )
    buttons.append([InlineKeyboardButton("\u2b05\ufe0f بازگشت", callback_data="section:currencies")])
    return InlineKeyboardMarkup(buttons)


def back_button() -> InlineKeyboardMarkup:
    """Single 'Back' button to return to the main menu."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("\u2b05\ufe0f بازگشت به منو", callback_data="menu")]]
    )
