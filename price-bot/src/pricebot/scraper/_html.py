"""Shared parsing utilities for alanchand.com HTML."""

from __future__ import annotations

import re

from bs4 import Tag

TREND_CLASSES = {
    "up": "up",
    "down": "down",
    "no_change": "no_change",
}

AttributeValueList = list[str]

_WHITESPACE_RE = re.compile(r"\s+")


def clean(text: str) -> str:
    """Collapse whitespace runs and trim."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def extract_trend(tag: Tag) -> str:
    """Read the CSS class of a price span to determine the trend."""
    classes: AttributeValueList = list(tag.get("class") or [])
    for cls in classes:
        if cls in TREND_CLASSES:
            return cls
    return "no_change"


def trend_from_container(tag: Tag) -> str:
    """Trend of a cell whose price span is nested inside (e.g. ``td.sellPrice``)."""
    span = tag.select_one("span.priceSymbol")
    return extract_trend(span) if span is not None else extract_trend(tag)
