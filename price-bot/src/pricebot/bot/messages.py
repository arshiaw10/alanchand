"""Render Telegram messages from a market snapshot."""

from __future__ import annotations

from pricebot.models import TREND_DOWN, TREND_FLAT, TREND_UP, MarketData

_TREND_ICONS = {
    TREND_UP: "\U0001f53c",       # 📈
    TREND_DOWN: "\U0001f53d",     # 📉
    TREND_FLAT: "\u2796",         # ➖
}

_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━"
_RULE = "────────────────────────────"

_NO_DATA = "\u26a0\ufe0f هنوز داده‌ای موجود نیست.\nلطفاً منتظر اولین دریافت بمانید."


def _icon(trend: str) -> str:
    return _TREND_ICONS.get(trend, "")


def _currency_block(c: dict) -> list[str]:
    return [
        f"\U0001f4b1 {c['name']} {_icon(c.get('trend', ''))}",
        f"    خرید: {c.get('buy_price', '-')}",
        f"    فروش: {c.get('sell_price', '-')}",
        f"    نرخ دلار: {c.get('usd_rate', '-')}",
    ]


def _gold_block(g: dict) -> str:
    return f"    {g['name']}: {g.get('price', '-')} {_icon(g.get('trend', ''))}"


def _crypto_block(c: dict) -> list[str]:
    symbol = f" ({c['symbol']})" if c.get("symbol") else ""
    return [
        f"{c['name']}{symbol} {_icon(c.get('trend', ''))}",
        f"    تومان: {c.get('price_toman', '-')}",
        f"    دلار: {c.get('price_usd', '-')}",
    ]


def _section_dicts(data: MarketData, section: str) -> list[dict]:
    if section == "currencies":
        return [vars(c) for c in data.currencies]
    if section == "gold":
        return [vars(g) for g in data.gold]
    if section == "crypto":
        return [vars(c) for c in data.crypto]
    raise ValueError(f"Unknown section: {section!r}")


def render_welcome() -> str:
    return (
        "\U0001f44b به ربات قیمت بازار خوش آمدید!\n"
        f"{_SEPARATOR}\n"
        "قیمت‌های لحظه‌ای ارز، طلا و رمزارز\n"
        "از alanchand.com\n\n"
        "یکی از بخش‌های زیر را انتخاب کنید:"
    )


def render_no_data(section_label: str = "") -> str:
    prefix = f"\u26a0\ufe0f {section_label} " if section_label else "\u26a0\ufe0f "
    return f"{prefix}داده‌ای موجود نیست. لطفاً چند لحظه بعد دوباره تلاش کنید."


def render_section(data: MarketData, section: str) -> str:
    """Render one section: currencies, gold, or crypto."""
    items = _section_dicts(data, section)
    if not items:
        return render_no_data()

    headers = {
        "currencies": "\U0001f4b5 ارزها",
        "gold": "\U0001f947 طلا و سکه",
        "crypto": "\u20bf رمزارز",
    }
    lines = [headers[section], _SEPARATOR, ""]
    if section == "currencies":
        for item in items:
            lines.extend(_currency_block(item))
            lines.append("")
    elif section == "gold":
        lines.extend(_gold_block(item) for item in items)
    else:
        for item in items:
            lines.extend(_crypto_block(item))
            lines.append("")
    return "\n".join(lines).rstrip()


def render_full_report(data: MarketData) -> str:
    """Render the combined market report."""
    if data.is_empty():
        return _NO_DATA

    lines = [
        "\U0001f4ca گزارش بازار",
        _SEPARATOR,
        f"\U0001f552 آخرین به‌روزرسانی: {data.updated_at or 'نامشخص'}",
        "",
    ]
    for section in ("currencies", "gold", "crypto"):
        if _section_dicts(data, section):
            lines.append(render_section(data, section))
            lines.append("")
    return "\n".join(lines).rstrip()


def render_single_currency(data: MarketData, index: int) -> str | None:
    """Render one currency detail card, or None if the index is out of range."""
    if index < 0 or index >= len(data.currencies):
        return None
    c = vars(data.currencies[index])
    return "\n".join(
        [
            f"\U0001f4b1 {c['name']} {_icon(c.get('trend', ''))}",
            _SEPARATOR,
            "",
            *_currency_block(c)[1:],
        ]
    )


def render_status(
    data: MarketData,
    last_scrape: str,
    next_run: str,
    last_error: str | None,
) -> str:
    """Render the bot status card."""
    lines = [
        "\u2139\ufe0f وضعیت ربات",
        _SEPARATOR,
        "",
        "\U0001f552 آخرین دریافت:",
        f"    {last_scrape or 'هنوز انجام نشده'}",
        "",
        "\u23f0 دریافت بعدی:",
        f"    {next_run or 'در انتظار'}",
        "",
        "\U0001f4ca تعداد آیتم‌ها:",
        f"    ارزها: {len(data.currencies)}",
        f"    طلا و سکه: {len(data.gold)}",
        f"    رمزارزها: {len(data.crypto)}",
    ]
    if last_error:
        lines.append(f"\n\u26a0\ufe0f آخرین خطا:\n    {last_error}")
    return "\n".join(lines)
