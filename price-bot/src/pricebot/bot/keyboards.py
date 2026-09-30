"""Telegram inline keyboards."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SECTION_CURRENCIES = "section:currencies"
SECTION_GOLD = "section:gold"
SECTION_CRYPTO = "section:crypto"
SECTION_ALL = "section:all"
SECTION_STATUS = "section:status"
MENU = "menu"
CURRENCY_PREFIX = "currency:"


def main_menu() -> InlineKeyboardMarkup:
    """Primary navigation keyboard."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("\U0001f4b5 ارزها", callback_data=SECTION_CURRENCIES),
                InlineKeyboardButton("\U0001f947 طلا و سکه", callback_data=SECTION_GOLD),
            ],
            [
                InlineKeyboardButton("\u20bf رمزارز", callback_data=SECTION_CRYPTO),
                InlineKeyboardButton("\U0001f30d همه بازارها", callback_data=SECTION_ALL),
            ],
            [
                InlineKeyboardButton("\u2139\ufe0f وضعیت", callback_data=SECTION_STATUS),
            ],
        ]
    )


def currency_list(names: list[str]) -> InlineKeyboardMarkup:
    """One button per currency, plus a back button."""
    rows = [
        [InlineKeyboardButton(name, callback_data=f"{CURRENCY_PREFIX}{i}")]
        for i, name in enumerate(names)
    ]
    rows.append([InlineKeyboardButton("\u2b05\ufe0f بازگشت", callback_data=SECTION_CURRENCIES)])
    return InlineKeyboardMarkup(rows)


def back_to_menu() -> InlineKeyboardMarkup:
    """Single back button returning to the main menu."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("\u2b05\ufe0f بازگشت به منو", callback_data=MENU)]]
    )
