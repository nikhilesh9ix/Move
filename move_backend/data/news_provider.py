"""News and sentiment signals via yfinance with TTL cache.

get_news_signal(stock)  → Optional[NewsSignal]   (async, cached 600s)
"""
from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Tuple

from core.logging import get_logger
from models.schemas import NewsSignal

logger = get_logger(__name__)

_NEWS_CACHE_TTL = 600   # 10 minutes — news is slow-moving

# ---------------------------------------------------------------------------
# Keyword sentiment
# ---------------------------------------------------------------------------

_POSITIVE: frozenset[str] = frozenset({
    "beat", "beats", "surges", "surge", "jumps", "jump", "rises", "rise",
    "gain", "gains", "profit", "profits", "upgrade", "upgraded", "outperform",
    "strong", "record", "high", "bullish", "buy", "positive", "growth",
    "expansion", "rally", "rallies", "exceeds", "exceed", "raises", "raised",
})

_NEGATIVE: frozenset[str] = frozenset({
    "miss", "misses", "falls", "fall", "drops", "drop", "declines", "decline",
    "loss", "losses", "downgrade", "downgraded", "underperform", "weak",
    "low", "bearish", "sell", "negative", "shrinks", "shrink", "cuts", "cut",
    "concern", "concerns", "warning", "warns", "below", "disappoints",
    "disappoint", "disappointing", "layoffs", "layoff", "slowdown",
})


def _score_headline(headline: str) -> float:
    """Return sentiment in [−1, +1] based on keyword overlap."""
    words = set(headline.lower().split())
    pos_hits = len(words & _POSITIVE)
    neg_hits = len(words & _NEGATIVE)
    total = pos_hits + neg_hits
    if total == 0:
        return 0.0
    return round((pos_hits - neg_hits) / total, 2)


# ---------------------------------------------------------------------------
# TTL Cache
# ---------------------------------------------------------------------------

class _TTLCache:
    def __init__(self) -> None:
        self._store: Dict[str, Tuple[object, float]] = {}

    def get(self, key: str) -> Optional[object]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: object, ttl: float) -> None:
        self._store[key] = (value, time.monotonic() + ttl)


_news_cache = _TTLCache()


# ---------------------------------------------------------------------------
# yfinance fetch (blocking — runs in executor)
# ---------------------------------------------------------------------------

def _fetch_news_sync(stock: str) -> Optional[NewsSignal]:
    """Blocking yfinance news call — must run in executor."""
    import yfinance as yf

    # Re-use the same NSE mapping from market_provider
    from data.market_provider import _to_yf_ticker
    yf_ticker = _to_yf_ticker(stock)

    try:
        ticker = yf.Ticker(yf_ticker)
        news_items = ticker.news
        if not news_items:
            logger.info("yf_news=empty ticker=%s", stock)
            return None

        # Pick the most recent article
        latest = news_items[0]
        headline = latest.get("content", {}).get("title", "") or latest.get("title", "")
        if not headline:
            return None

        url = (
            latest.get("content", {}).get("canonicalUrl", {}).get("url", "")
            or latest.get("link", "")
        )

        sentiment = _score_headline(headline)
        logger.info(
            "yf_news=fetched ticker=%s headline_len=%d sentiment=%.2f",
            stock, len(headline), sentiment,
        )
        return NewsSignal(
            stock=stock.upper(),
            headline=headline,
            sentiment=sentiment,
            url=url,
        )
    except Exception as exc:
        logger.warning("yf_news=error ticker=%s error=%s", stock, exc)
        return None


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------

async def get_news_signal(stock: str) -> Optional[NewsSignal]:
    """Return the latest NewsSignal for stock, or None if unavailable."""
    cache_key = f"news:{stock.upper()}"
    cached = _news_cache.get(cache_key)
    if cached is not None:
        return cached  # type: ignore[return-value]

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _fetch_news_sync, stock)

    if result is not None:
        _news_cache.set(cache_key, result, _NEWS_CACHE_TTL)
    return result
