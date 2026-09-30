"""JSON-file repository for market snapshots."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from pricebot.models import MarketData

logger = logging.getLogger(__name__)


class MarketDataRepository:
    """Read/write normalized market data as an atomically-replaced JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def save(self, data: MarketData) -> None:
        """Overwrite the cache atomically (write-then-rename)."""
        tmp = self._path.with_suffix(".tmp")
        try:
            tmp.write_text(
                json.dumps(data.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp, self._path)
        except OSError:
            logger.exception("Failed to persist market data to %s", self._path)
            tmp.unlink(missing_ok=True)

    def load(self) -> MarketData | None:
        """Return the cached snapshot, or None when missing or corrupted."""
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError:
            logger.exception("Failed to read %s", self._path)
            return None

        try:
            return MarketData.from_dict(json.loads(raw))
        except (json.JSONDecodeError, TypeError, ValueError):
            logger.exception("Corrupted cache file at %s – deleting", self._path)
            self._path.unlink(missing_ok=True)
            return None
