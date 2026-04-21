from __future__ import annotations

import asyncio
import math
import random
import time
from datetime import datetime
from typing import Dict, List

from core.logging import get_logger
from data.market_provider import get_price_change
from services.connection_manager import manager
from services.event_store import event_store
from services.orchestrator import run_analysis

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WATCHED_TICKERS: List[str] = ["TCS", "INFY", "RELIANCE", "HDFC", "WIPRO"]
POLL_INTERVAL_SECONDS: float = 20.0       # real API: slower poll to avoid rate limits
MOVEMENT_THRESHOLD_PCT: float = 0.8       # real market data: lower threshold

# Must match the date the mock data is seeded with for consistent demo output
_ANALYSIS_DATE = "2026-04-20"


class PriceWatcher:
    """Async background task that simulates price monitoring.

    Every POLL_INTERVAL_SECONDS it samples a price change per ticker using a
    deterministic Normal(0, 2%) distribution seeded by (ticker, time_bucket).
    When |change| crosses MOVEMENT_THRESHOLD_PCT the full causal pipeline is
    triggered, the result is stored in EventStore, and all WebSocket clients
    are notified.

    Restarts automatically on unexpected crashes (CancelledError propagates
    cleanly for graceful shutdown).
    """

    def __init__(
        self,
        tickers: List[str] = WATCHED_TICKERS,
        poll_interval: float = POLL_INTERVAL_SECONDS,
        threshold: float = MOVEMENT_THRESHOLD_PCT,
    ) -> None:
        self.tickers = tickers
        self.poll_interval = poll_interval
        self.threshold = threshold
        self._previous: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Price simulation
    # ------------------------------------------------------------------

    def _simulate_price_change(self, ticker: str) -> float:
        """Deterministic ~Normal(0, 2%) change for a given (ticker, time_bucket).

        The time_bucket flips every poll_interval seconds so each poll sees a
        fresh value while remaining stable within a single poll cycle.
        """
        t_bucket = int(time.time() / self.poll_interval)
        rng = random.Random(hash(f"{ticker}:{t_bucket}"))
        # Box–Muller transform — no external dependency
        u1 = max(rng.random(), 1e-10)
        u2 = rng.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)
        return round(z * 2.0, 2)  # scale to std=2%

    # ------------------------------------------------------------------
    # Price resolution: real data with simulation fallback
    # ------------------------------------------------------------------

    async def _get_price_change(self, ticker: str) -> float:
        """Try live yfinance data; fall back to Box-Muller simulation."""
        try:
            real_change = await get_price_change(ticker)
            if real_change is not None:
                logger.debug("watcher=real_price ticker=%s change=%.2f%%", ticker, real_change)
                return real_change
        except Exception as exc:
            logger.debug("watcher=real_price_error ticker=%s error=%s", ticker, exc)
        return self._simulate_price_change(ticker)

    # ------------------------------------------------------------------
    # Per-ticker processing
    # ------------------------------------------------------------------

    async def _process_ticker(self, ticker: str) -> None:
        change = await self._get_price_change(ticker)
        prev = self._previous.get(ticker)
        self._previous[ticker] = change

        # Skip if below threshold
        if abs(change) < self.threshold:
            return

        # Skip if same bucket already processed (value hasn't changed)
        if prev is not None and abs(change - prev) < 0.01:
            return

        logger.info(
            "watcher=trigger ticker=%s change=%.2f%% threshold=%.1f%%",
            ticker,
            change,
            self.threshold,
        )

        try:
            analysis = await run_analysis(ticker, _ANALYSIS_DATE)
        except Exception as exc:
            logger.error("watcher=analysis_error ticker=%s error=%s", ticker, exc)
            return

        event: Dict = {
            "type": "analysis_update",
            "ticker": ticker,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "price_change": change,
            "attribution": [a.model_dump() for a in analysis.attribution],
            "explanation": analysis.explanation,
            "historical_hint": analysis.historical_hint,
            "actionable_insight": analysis.actionable_insight,
            "confidence_pct": analysis.confidence_pct,
        }

        await event_store.put(ticker, event)
        await manager.broadcast(event)

        logger.info(
            "watcher=broadcast_complete ticker=%s ws_clients=%d",
            ticker,
            manager.count,
        )

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    async def _watch_loop(self) -> None:
        while True:
            await asyncio.sleep(self.poll_interval)
            for ticker in self.tickers:
                await self._process_ticker(ticker)

    async def start(self) -> None:
        """Entry point. Runs forever; restarts on crash; propagates CancelledError."""
        logger.info(
            "watcher=start tickers=%s interval=%.0fs threshold=%.1f%%",
            self.tickers,
            self.poll_interval,
            self.threshold,
        )
        while True:
            try:
                await self._watch_loop()
            except asyncio.CancelledError:
                logger.info("watcher=stopped")
                raise
            except Exception as exc:
                logger.error("watcher=crashed error=%s restarting_in=5s", exc)
                await asyncio.sleep(5)


# Module-level singleton
price_watcher = PriceWatcher()
