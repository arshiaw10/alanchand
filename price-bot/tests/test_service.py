"""Tests for MarketService and message rendering."""

from __future__ import annotations

from pathlib import Path

from pricebot.bot import messages as fmt
from pricebot.models import CryptoItem, Currency, GoldItem, MarketData
from pricebot.scraper.scraper import MarketScraper, ScrapeError
from pricebot.services.market_service import MarketService
from pricebot.storage.repository import MarketDataRepository


def _sample() -> MarketData:
    return MarketData(
        updated_at="۱۴۰۳/۰۴/۱۵ ۱۰:۳۰",
        scraped_at="2026-09-30T10:00:00+00:00",
        currencies=[
            Currency(name="دلار آمریکا", buy_price="61,500", sell_price="61,700", usd_rate="1"),
        ],
        gold=[GoldItem(name="سکه امامی", price="42,000,000")],
        crypto=[CryptoItem(name="بیت‌کوین", price_toman="4,250,000,000", price_usd="63,950$")],
    )


def _service(tmp_path: Path, data: MarketData | None) -> MarketService:
    repo = MarketDataRepository(tmp_path / "data.json")
    if data is not None:
        repo.save(data)

    class _StubScraper(MarketScraper):
        def __init__(self) -> None:  # bypass parent init on purpose
            pass

        def scrape(self) -> MarketData:
            raise ScrapeError("stub")

    return MarketService(repository=repo, scraper=_StubScraper())


def test_snapshot_loads_from_disk(tmp_path: Path) -> None:
    service = _service(tmp_path, _sample())
    assert len(service.snapshot().currencies) == 1
    assert service.snapshot().currencies[0].name == "دلار آمریکا"


def test_snapshot_empty_when_no_data(tmp_path: Path) -> None:
    service = _service(tmp_path, None)
    assert service.snapshot().is_empty()


def test_run_scrape_failure_records_error(tmp_path: Path) -> None:
    service = _service(tmp_path, None)
    assert service.run_scrape() is False
    assert service.last_error is not None


# -- message rendering -------------------------------------------------------


def test_render_full_report_contains_sections() -> None:
    text = fmt.render_full_report(_sample())
    assert "گزارش بازار" in text
    assert "دلار آمریکا" in text
    assert "سکه امامی" in text
    assert "بیت‌کوین" in text


def test_render_full_report_empty() -> None:
    assert "موجود نیست" in fmt.render_full_report(unknown := MarketData("", ""))
    assert unknown is not None


def test_render_single_currency_out_of_range() -> None:
    assert fmt.render_single_currency(_sample(), 99) is None


def test_render_single_currency_valid() -> None:
    text = fmt.render_single_currency(_sample(), 0)
    assert text is not None
    assert "دلار آمریکا" in text
    assert "خرید" in text


def test_render_section_empty_warns() -> None:
    empty = MarketData(updated_at="", scraped_at="")
    assert "موجود نیست" in fmt.render_section(empty, "currencies")


def test_render_status_contains_counts() -> None:
    text = fmt.render_status(_sample(), last_scrape="10:00", next_run="10:05", last_error=None)
    assert "ارزها: 1" in text
    assert "طلا و سکه: 1" in text
    assert "رمزارزها: 1" in text
