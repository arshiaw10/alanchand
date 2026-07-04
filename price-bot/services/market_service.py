"""Business logic that ties scraping, storage, and formatting together."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scraper.scraper import scrape_all
from storage.repository import MarketDataRepository

logger = logging.getLogger(__name__)

_TREND = {
    "up": "\U0001f53c",
    "down": "\U0001f53d",
    "no_change": "\u2796",
}


class MarketService:
    """Facade used by bot handlers and the scheduler."""

    def __init__(self, repo: MarketDataRepository | None = None) -> None:
        self.repo = repo or MarketDataRepository()
        self._last_error: str | None = None
        self._next_run: datetime | None = None

    # ------------------------------------------------------------------
    # Scraper trigger
    # ------------------------------------------------------------------

    def run_scrape(self) -> bool:
        """Execute one scrape cycle.  Returns True on success."""
        try:
            data = scrape_all()
            self.repo.save(data)
            self._last_error = None
            return True
        except Exception as exc:
            self._last_error = str(exc)
            logger.exception("Scrape failed")
            return False

    # ------------------------------------------------------------------
    # Accessors for bot handlers
    # ------------------------------------------------------------------

    def get_currencies(self) -> list[dict[str, Any]]:
        data = self.repo.load() or {}
        return data.get("currencies", [])

    def get_gold(self) -> list[dict[str, Any]]:
        data = self.repo.load() or {}
        return data.get("gold", [])

    def get_crypto(self) -> list[dict[str, Any]]:
        data = self.repo.load() or {}
        return data.get("crypto", [])

    def get_full_report(self) -> str:
        data = self.repo.load()
        if not data:
            return "\u26a0\ufe0f هنوز داده‌ای موجود نیست.\nلطفاً منتظر اولین دریافت بمانید."

        updated = data.get("updated_at", "N/A")
        lines = [
            "\U0001f4ca گزارش بازار",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"\U0001f552 آخرین به‌روزرسانی: {updated}",
            "",
        ]

        currencies = data.get("currencies", [])
        if currencies:
            lines.append("\U0001f4b5 ارزها")
            lines.append("────────────────────────────")
            for c in currencies:
                trend = _TREND.get(c.get("trend", "no_change"), "")
                lines.append(
                    f"\U0001f4b1 {c['name']} {trend}\n"
                    f"    خرید: {c['buy_price']}\n"
                    f"    فروش: {c['sell_price']}\n"
                    f"    نرخ دلار: {c['usd_rate']}"
                )
            lines.append("")

        gold = data.get("gold", [])
        if gold:
            lines.append("\U0001f947 طلا و سکه")
            lines.append("────────────────────────────")
            for g in gold:
                trend = _TREND.get(g.get("trend", "no_change"), "")
                lines.append(f"    {g['name']}: {g['price']} {trend}")
            lines.append("")

        crypto = data.get("crypto", [])
        if crypto:
            lines.append("\u20bf رمزارز")
            lines.append("────────────────────────────")
            for c in crypto:
                trend = _TREND.get(c.get("trend", "no_change"), "")
                sym = f" ({c['symbol']})" if c.get("symbol") else ""
                lines.append(
                    f"    {c['name']}{sym} {trend}\n"
                    f"    تومان: {c['price_toman']}\n"
                    f"    دلار: {c['price_usd']}"
                )

        return "\n".join(lines)

    def get_section(self, key: str) -> str:
        """Return a formatted block for a single section."""
        formatters = {
            "currencies": self._format_currencies,
            "gold": self._format_gold,
            "crypto": self._format_crypto,
        }
        fn = formatters.get(key)
        if fn is None:
            return "بخش نامعتبر."
        return fn()

    def get_single_currency(self, index: int) -> str | None:
        """Return formatted detail for a single currency by index."""
        items = self.get_currencies()
        if index < 0 or index >= len(items):
            return None
        c = items[index]
        trend = _TREND.get(c.get("trend", "no_change"), "")
        return (
            f"\U0001f4b1 {c['name']} {trend}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"\n"
            f"    \U0001f4b5 خرید: {c['buy_price']}\n"
            f"    \U0001f4b5 فروش: {c['sell_price']}\n"
            f"    \U0001f4b1 نرخ دلار: {c['usd_rate']}"
        )

    def status_text(self) -> str:
        counts = self.repo.counts()
        last = self.repo.last_scrape_time()
        next_run = self._next_run

        lines = [
            "\u2139\ufe0f وضعیت ربات",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"\U0001f552 آخرین دریافت:",
            f"    {last.strftime('%Y-%m-%d %H:%M:%S UTC') if last else 'هنوز انجام نشده'}",
            "",
            f"\u23f0 دریافت بعدی:",
            f"    {next_run.strftime('%H:%M UTC') if next_run else 'در انتظار'}",
            "",
            f"\U0001f4ca تعداد آیتم‌ها:",
            f"    ارزها: {counts['currencies']}",
            f"    طلا و سکه: {counts['gold']}",
            f"    رمزارزها: {counts['crypto']}",
        ]
        if self._last_error:
            lines.append(f"\n\u26a0\ufe0f آخرین خطا:\n    {self._last_error}")
        return "\n".join(lines)

    def set_next_run(self, dt: datetime) -> None:
        self._next_run = dt

    # ------------------------------------------------------------------
    # Private formatters
    # ------------------------------------------------------------------

    def _format_currencies(self) -> str:
        items = self.get_currencies()
        if not items:
            return "\u26a0\ufe0f داده ارزی موجود نیست."
        lines = ["\U0001f4b5 ارزها", "━━━━━━━━━━━━━━━━━━━━━━━━", ""]
        for c in items:
            trend = _TREND.get(c.get("trend", "no_change"), "")
            lines.append(
                f"\U0001f4b1 {c['name']} {trend}\n"
                f"    خرید: {c['buy_price']}\n"
                f"    فروش: {c['sell_price']}\n"
                f"    نرخ دلار: {c['usd_rate']}"
            )
            lines.append("")
        return "\n".join(lines)

    def _format_gold(self) -> str:
        items = self.get_gold()
        if not items:
            return "\u26a0\ufe0f داده طلا و سکه موجود نیست."
        lines = ["\U0001f947 طلا و سکه", "━━━━━━━━━━━━━━━━━━━━━━━━", ""]
        for g in items:
            trend = _TREND.get(g.get("trend", "no_change"), "")
            lines.append(f"    {g['name']}: {g['price']} {trend}")
        return "\n".join(lines)

    def _format_crypto(self) -> str:
        items = self.get_crypto()
        if not items:
            return "\u26a0\ufe0f داده رمزارز موجود نیست."
        lines = ["\u20bf رمزارز", "━━━━━━━━━━━━━━━━━━━━━━━━", ""]
        for c in items:
            trend = _TREND.get(c.get("trend", "no_change"), "")
            sym = f" ({c['symbol']})" if c.get("symbol") else ""
            lines.append(
                f"    {c['name']}{sym} {trend}\n"
                f"    تومان: {c['price_toman']}\n"
                f"    دلار: {c['price_usd']}"
            )
            lines.append("")
        return "\n".join(lines)
