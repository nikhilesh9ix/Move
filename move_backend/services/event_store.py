from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from core.logging import get_logger

logger = get_logger(__name__)


class EventStore:
    """In-memory store for the latest causal analysis event per ticker.

    Thread-safe via asyncio.Lock. Module singleton is `event_store`.
    """

    def __init__(self, max_recent: int = 20) -> None:
        self._by_ticker: Dict[str, Dict[str, Any]] = {}
        self._recent: List[Dict[str, Any]] = []
        self._max_recent = max_recent
        self._lock = asyncio.Lock()

    async def put(self, ticker: str, event: Dict[str, Any]) -> None:
        """Store event for ticker and append to recency list."""
        async with self._lock:
            self._by_ticker[ticker] = event
            self._recent.append(event)
            if len(self._recent) > self._max_recent:
                self._recent.pop(0)
        logger.info("event_store=put ticker=%s total_tickers=%d", ticker, len(self._by_ticker))

    def get(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Latest event for ticker, or None."""
        return self._by_ticker.get(ticker)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Snapshot of latest event per ticker."""
        return dict(self._by_ticker)

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Last n events across all tickers, newest first."""
        return list(reversed(self._recent[-n:]))


# Module-level singleton — import this everywhere
event_store = EventStore()
