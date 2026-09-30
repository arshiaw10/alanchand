"""Unit tests for the HTML parsers."""

from __future__ import annotations

from bs4 import BeautifulSoup

from pricebot.scraper.crypto_parser import parse_crypto
from pricebot.scraper.currency_parser import parse_currencies
from pricebot.scraper.gold_parser import parse_gold

CURRENCY_HTML = """
<table class="CurrencyTbl">
  <tbody>
    <tr>
      <td class="currName">دلار آمریکا</td>
      <td class="buyPrice">61,500</td>
      <td class="sellPrice"><span class="priceSymbol up">61,700</span></td>
      <td class="usdRate">1</td>
    </tr>
    <tr>
      <td class="currName">یورو</td>
      <td class="buyPrice">66,200</td>
      <td class="sellPrice"><span class="priceSymbol down">66,900</span></td>
      <td class="usdRate">1.09</td>
    </tr>
    <tr><td>broken row</td></tr>
  </tbody>
</table>
"""

GOLD_HTML = """
<div class="goldCard">
  <h3><a>سکه امامی</a></h3>
  <span class="priceSymbol up">42,000,000</span>
</div>
<div class="goldCard">
  <h3><a>گرم طلای ۱۸ عیار</a></h3>
  <span class="priceSymbol no_change">3,850,000</span>
</div>
"""

CRYPTO_HTML = """
<section class="cryptoPrice">
  <div class="card shadow">
    <h3><a>بیت‌کوین</a></h3>
    <span class="text-secondary">BTC</span>
    <span class="fw-bold priceSymbol up">4,250,000,000</span>
    <span class="fw-normal">63,950.20$</span>
  </div>
</section>
"""


def test_parse_currencies() -> None:
    soup = BeautifulSoup(CURRENCY_HTML, "lxml")
    rows = parse_currencies(soup)
    assert len(rows) == 2
    usd, eur = rows
    assert usd.name == "دلار آمریکا"
    assert usd.buy_price == "61,500"
    assert usd.sell_price == "61,700"
    assert usd.trend == "up"
    assert eur.trend == "down"
    assert eur.usd_rate == "1.09"


def test_parse_currencies_missing_rate_defaults_to_dash() -> None:
    soup = BeautifulSoup(
        '<table class="CurrencyTbl"><tbody><tr>'
        '<td class="currName">درهم</td>'
        '<td class="buyPrice">16,700</td>'
        '<td class="sellPrice">16,900</td>'
        "</tr></tbody></table>",
        "lxml",
    )
    rows = parse_currencies(soup)
    assert len(rows) == 1
    assert rows[0].usd_rate == "-"


def test_parse_gold() -> None:
    soup = BeautifulSoup(GOLD_HTML, "lxml")
    items = parse_gold(soup)
    assert len(items) == 2
    assert items[0].name == "سکه امامی"
    assert items[0].price == "42,000,000"
    assert items[0].trend == "up"
    assert items[1].trend == "no_change"


def test_parse_crypto() -> None:
    soup = BeautifulSoup(CRYPTO_HTML, "lxml")
    items = parse_crypto(soup)
    assert len(items) == 1
    btc = items[0]
    assert btc.name == "بیت‌کوین"
    assert btc.symbol == "BTC"
    assert btc.price_toman == "4,250,000,000"
    assert btc.price_usd == "63,950.20$"
    assert btc.trend == "up"


def test_parse_crypto_missing_section_returns_empty() -> None:
    soup = BeautifulSoup("<html><body></body></html>", "lxml")
    assert parse_crypto(soup) == []
