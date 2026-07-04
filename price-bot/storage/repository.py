"""JSON-file repository for market data."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import Config

logger = logging.getLogger(__name__)


class MarketDataRepository:
    """Read/write normalized market data as a JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Config.DATA_FILE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, data: dict[str, Any]) -> None:
        """Overwrite the cache with *data* atomically (write-then-rename)."""
        tmp = self._path.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._path)
            logger.info("Market data saved (%s)", self._path)
        except OSError:
            logger.exception("Failed to persist market data")
            if tmp.exists():
                tmp.unlink(missing_ok=True)

    def load(self) -> dict[str, Any] | None:
        """Return cached data or *None* when unavailable / corrupted."""
        if not self._path.exists():
            return None
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.exception("Corrupted cache file – deleting")
            self._path.unlink(missing_ok=True)
            return None

    def last_scrape_time(self) -> datetime | None:
        data = self.load()
        if data and "scraped_at" in data:
            try:
                return datetime.fromisoformat(data["scraped_at"])
            except (ValueError, TypeError):
                return None
        return None

    def counts(self) -> dict[str, int]:
        data = self.load() or {}
        return {
            "currencies": len(data.get("currencies", [])),
            "gold": len(data.get("gold", [])),
            "crypto": len(data.get("crypto", [])),
        }
