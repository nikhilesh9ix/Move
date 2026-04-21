"""Real-world price data via yfinance with TTL cache and deterministic mock fallback.

get_price_data(stock)       → PriceData   (async, cached 60s)
get_price_change(ticker)    → float | None  (latest % change, cached 30s)
"""
from __future__ import annotations

import asyncio
import hashlib
import random
import time
from datetime import datetime
from typing import Dict, Optional, Tuple

from core.logging import get_logger
from models.schemas import PriceData

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Ticker mapping — Yahoo Finance suffixes for NSE tickers
# ---------------------------------------------------------------------------
_NSE_OVERRIDES: Dict[str, str] = {
    "TCS":      "TCS.NS",
    "INFY":     "INFY.NS",
    "RELIANCE": "RELIANCE.NS",
    "HDFC":     "HDFCBANK.NS",
    "WIPRO":    "WIPRO.NS",
    "NIFTY":    "^NSEI",
    "SENSEX":   "^BSESN",
}

_PRICE_CACHE_TTL = 60   # seconds
_CHANGE_CACHE_TTL = 30  # seconds for live % change polls

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

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)


_price_cache = _TTLCache()
_change_cache = _TTLCache()


# ---------------------------------------------------------------------------
# Mock fallback — deterministic, seeded by (stock, hour)
# ---------------------------------------------------------------------------

def _mock_price_data(stock: str) -> PriceData:
    hour_bucket = datetime.utcnow().strftime("%Y%m%d%H")
    seed_bytes = f"{stock.upper()}{hour_bucket}".encode()
    seed_int = int(hashlib.md5(seed_bytes).hexdigest(), 16) % (2**32)
    rng = random.Random(seed_int)

    price_change = round(rng.uniform(-6.0, 6.0), 2)
    base_price   = round(rng.uniform(200.0, 4000.0), 2)
    volatility   = round(1.5 + rng.uniform(0.0, 2.5), 2)
    volume       = rng.randint(500_000, 50_000_000)

    return PriceData(
        stock=stock.upper(),
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        price_change=price_change,
        base_price=base_price,
        volatility=volatility,
        volume=volume,
        direction="up" if price_change >= 0 else "down",
        source="mock",
    )


# ---------------------------------------------------------------------------
# yfinance fetch (blocking — runs in executor)
# ---------------------------------------------------------------------------

def _to_yf_ticker(stock: str) -> str:
    upper = stock.upper()
    return _NSE_OVERRIDES.get(upper, upper)


def _fetch_yf_sync(stock: str) -> Optional[PriceData]:
    """Blocking yfinance call — must run in executor."""
    import yfinance as yf  # lazy import; avoid import cost when using mock

    yf_ticker = _to_yf_ticker(stock)
    try:
        hist = yf.Ticker(yf_ticker).history(period="5d")
        if hist.empty or len(hist) < 2:
            logger.warning("yf=no_data ticker=%s yf_ticker=%s", stock, yf_ticker)
            return None

        close_prices = hist["Close"]
        prev_close = float(close_prices.iloc[-2])
        last_close  = float(close_prices.iloc[-1])
        volume      = int(hist["Volume"].iloc[-1])

        if prev_close == 0:
            return None

        price_change = round((last_close - prev_close) / prev_close * 100, 2)

        # Intraday high-low as volatility proxy
        day = hist.iloc[-1]
        high = float(day["High"])
        low  = float(day["Low"])
        volatility = round((high - low) / last_close * 100, 2) if last_close else 2.0

        logger.info(
            "yf=fetch_ok ticker=%s yf_ticker=%s price_change=%.2f",
            stock, yf_ticker, price_change,
        )
        return PriceData(
            stock=stock.upper(),
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            price_change=price_change,
            base_price=round(last_close, 2),
            volatility=volatility,
            volume=volume,
            direction="up" if price_change >= 0 else "down",
            source="yfinance",
        )
    except Exception as exc:
        logger.warning("yf=fetch_error ticker=%s error=%s", stock, exc)
        return None


def _fetch_yf_change_sync(stock: str) -> Optional[float]:
    """Lightweight blocking call — returns % change only."""
    import yfinance as yf

    yf_ticker = _to_yf_ticker(stock)
    try:
        hist = yf.Ticker(yf_ticker).history(period="2d")
        if len(hist) < 2:
            return None
        prev = float(hist["Close"].iloc[-2])
        last = float(hist["Close"].iloc[-1])
        if prev == 0:
            return None
        return round((last - prev) / prev * 100, 2)
    except Exception as exc:
        logger.warning("yf=change_error ticker=%s error=%s", stock, exc)
        return None


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------

_YF_TIMEOUT_SECONDS = 4.0  # max wait per yfinance call before falling back to mock


async def get_price_data(stock: str) -> PriceData:
    """Return PriceData for stock. Tries yfinance first (4s max); falls back to mock."""
    cache_key = f"price:{stock.upper()}"
    cached = _price_cache.get(cache_key)
    if cached is not None:
        return cached  # type: ignore[return-value]

    loop = asyncio.get_event_loop()
    result: Optional[PriceData] = None
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _fetch_yf_sync, stock),
            timeout=_YF_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("yf=timeout stock=%s falling_back=mock", stock)
    except Exception as exc:
        logger.warning("yf=error stock=%s error=%s", stock, exc)

    if result is None:
        logger.info("price_provider=fallback_mock stock=%s", stock)
        result = _mock_price_data(stock)

    _price_cache.set(cache_key, result, _PRICE_CACHE_TTL)
    return result


async def get_price_change(ticker: str) -> Optional[float]:
    """Return latest % change for ticker. Returns None if unavailable (4s timeout)."""
    cache_key = f"change:{ticker.upper()}"
    cached = _change_cache.get(cache_key)
    if cached is not None:
        return cached  # type: ignore[return-value]

    loop = asyncio.get_event_loop()
    result: Optional[float] = None
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _fetch_yf_change_sync, ticker),
            timeout=_YF_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("yf=change_timeout ticker=%s", ticker)
    except Exception as exc:
        logger.warning("yf=change_error ticker=%s error=%s", ticker, exc)

    if result is not None:
        _change_cache.set(cache_key, result, _CHANGE_CACHE_TTL)
    return result
