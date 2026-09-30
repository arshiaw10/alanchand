"""Parse currency rows from alanchand.com HTML."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from pricebot.models import Currency
from pricebot.scraper._html import clean, trend_from_container

logger = logging.getLogger(__name__)


def parse_currencies(soup: BeautifulSoup) -> list[Currency]:
    """Extract currency rows from all ``table.CurrencyTbl`` tables."""
    currencies: list[Currency] = []

    for table in soup.select("table.CurrencyTbl"):
        for row in table.select("tbody tr"):
            name_el = row.select_one("td.currName")
            buy_el = row.select_one("td.buyPrice")
            sell_el = row.select_one("td.sellPrice")

            if not (name_el and buy_el and sell_el):
                continue

            rate_el = row.select_one("td.usdRate")
            currencies.append(
                Currency(
                    name=clean(name_el.get_text()),
                    buy_price=clean(buy_el.get_text()),
                    sell_price=clean(sell_el.get_text()),
                    usd_rate=clean(rate_el.get_text()) if rate_el else "-",
                    trend=trend_from_container(sell_el),
                )
            )

    logger.info("Parsed %d currencies", len(currencies))
    return currencies
