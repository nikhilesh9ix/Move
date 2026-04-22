"""Rich stock detail via yfinance — price history, fundamentals, technicals.

get_stock_detail(symbol) → StockDetailResponse | None   (async, cached 5 min)
"""
from __future__ import annotations

import asyncio
import time
from typing import Dict, List, Optional, Tuple

from core.logging import get_logger
from models.schemas import (
    FibLevel,
    PricePoint,
    RevenueEntry,
    StockBalanceResponse,
    StockDetailResponse,
    StockRatiosResponse,
    StockTechnicalResponse,
)

logger = get_logger(__name__)

_DETAIL_CACHE_TTL = 300  # 5 min
_YF_TIMEOUT = 10.0       # generous timeout — financials fetch is slow

# ---------------------------------------------------------------------------
# NSE ticker resolution
# ---------------------------------------------------------------------------

_NSE_SYMBOLS = {
    "TCS", "INFY", "WIPRO", "HDFCBANK", "ICICIBANK", "KOTAKBANK",
    "AXISBANK", "SBIN", "BAJFINANCE", "HINDUNILVR", "ITC", "TATASTEEL",
    "MARUTI", "SUNPHARMA", "NTPC", "ONGC", "POWERGRID", "ADANIENT",
    "ADANIPORTS", "LTIM", "TECHM", "HCLTECH", "BAJAJFINSV", "BHARTIARTL",
    "RELIANCE", "NESTLEIND", "ASIANPAINT", "TITAN", "ULTRACEMCO",
    "BRITANNIA", "DIVISLAB", "DRREDDY", "EICHERMOT", "HEROMOTOCO",
    "CIPLA", "APOLLOHOSP", "TATACONSUM", "INDUSINDBK", "JSWSTEEL",
    "TATAMOTORS", "LT", "M&M", "GRASIM", "BPCL", "COALINDIA",
}

_ALIAS: Dict[str, str] = {
    "HDFC":   "HDFCBANK",
    "ICICI":  "ICICIBANK",
    "KOTAK":  "KOTAKBANK",
    "AXIS":   "AXISBANK",
    "SBI":    "SBIN",
    "HCL":    "HCLTECH",
}


def _resolve_yf_ticker(symbol: str) -> str:
    upper = symbol.upper().strip()
    upper = _ALIAS.get(upper, upper)
    # Already qualified (e.g. TCS.NS, AAPL, BTC-USD, ^NSEI)
    if any(c in upper for c in (".", "^", "-")):
        return upper
    # Known NSE symbol
    if upper in _NSE_SYMBOLS:
        return f"{upper}.NS"
    # Unknown — return as-is (likely a US ticker); fallback to .NS tried in fetch
    return upper


# ---------------------------------------------------------------------------
# TTL cache
# ---------------------------------------------------------------------------

class _TTLCache:
    def __init__(self) -> None:
        self._store: Dict[str, Tuple[object, float]] = {}

    def get(self, key: str) -> Optional[object]:
        entry = self._store.get(key)
        if entry is None:
            return None
        val, exp = entry
        if time.monotonic() > exp:
            del self._store[key]
            return None
        return val

    def set(self, key: str, val: object, ttl: float) -> None:
        self._store[key] = (val, time.monotonic() + ttl)


_cache = _TTLCache()


# ---------------------------------------------------------------------------
# Pure-Python numeric helpers
# ---------------------------------------------------------------------------

def _rolling_avg(values: List[float], period: int) -> List[float]:
    result: List[float] = []
    for i in range(len(values)):
        window = values[max(0, i - period + 1): i + 1]
        result.append(sum(window) / len(window))
    return result


def _wilder_rsi(closes: List[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains  = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    return round(100.0 - 100.0 / (1.0 + avg_gain / avg_loss), 1)


def _support_resistance(closes: List[float]) -> Tuple[float, float]:
    return round(min(closes), 2), round(max(closes), 2)


def _fib_levels(support: float, resistance: float) -> List[FibLevel]:
    span = resistance - support
    return [
        FibLevel(level="23.6%", value=round(resistance - 0.236 * span, 2)),
        FibLevel(level="38.2%", value=round(resistance - 0.382 * span, 2)),
        FibLevel(level="50.0%", value=round(resistance - 0.500 * span, 2)),
        FibLevel(level="61.8%", value=round(resistance - 0.618 * span, 2)),
    ]


def _format_value(rupees_or_dollars: float, currency: str) -> str:
    """Format raw currency amount (debt/cash) as human-readable string."""
    if currency == "INR":
        cr = rupees_or_dollars / 1e7
        if cr >= 100_000:
            return f"₹{cr / 100_000:.2f}L Cr"
        if cr >= 1_000:
            return f"₹{cr:,.0f} Cr"
        return f"₹{cr:.0f} Cr"
    b = rupees_or_dollars / 1e9
    if b >= 1_000:
        return f"${b / 1_000:.2f}T"
    return f"${b:.2f}B"


def _format_market_cap(value: float, currency: str) -> str:
    if currency == "INR":
        cr = value / 1e7
        if cr >= 100_000:
            return f"₹{cr / 100_000:.1f}L Cr"
        return f"₹{cr / 1_000:.1f}k Cr"
    b = value / 1e9
    if b >= 1_000:
        return f"${b / 1_000:.2f}T"
    return f"${b:.2f}B"


def _health_score_and_label(
    cash: float, debt: float, de: float
) -> Tuple[int, str]:
    if cash > 0 and debt > 0:
        ratio = cash / debt
        score = min(95, max(15, int(50 + ratio * 25)))
    elif cash > 0 and debt == 0:
        score = 92
    elif de < 0.3:
        score = 80
    elif de < 0.8:
        score = 58
    else:
        score = 32
    label = "Strong" if score >= 70 else "Moderate" if score >= 45 else "Weak"
    return score, label


# ---------------------------------------------------------------------------
# Blocking yfinance fetch
# ---------------------------------------------------------------------------

def _nan_safe(v: object) -> float:
    """Return float or 0 if None/NaN."""
    if v is None:
        return 0.0
    try:
        f = float(v)  # type: ignore[arg-type]
        return f if f == f else 0.0  # NaN check
    except (TypeError, ValueError):
        return 0.0


def _fetch_sync(symbol: str) -> Optional[StockDetailResponse]:
    import yfinance as yf

    primary = _resolve_yf_ticker(symbol)
    # For ambiguous bare symbols, also try .NS suffix
    candidates = [primary]
    if "." not in primary and "^" not in primary:
        candidates.append(f"{primary}.NS")

    ticker_obj = None
    hist = None
    used_sym = primary

    for candidate in candidates:
        try:
            t = yf.Ticker(candidate)
            h = t.history(period="90d")
            if not h.empty and len(h) >= 10:
                ticker_obj = t
                hist = h
                used_sym = candidate
                break
        except Exception as exc:
            logger.debug("yf=history_error candidate=%s error=%s", candidate, exc)

    if hist is None or hist.empty or len(hist) < 10:
        logger.warning("stock_provider=no_data symbol=%s", symbol)
        return None

    currency = "INR" if used_sym.endswith(".NS") or used_sym.endswith(".BO") else "USD"

    # ── info dict ─────────────────────────────────────────────────────────
    info: dict = {}
    try:
        info = ticker_obj.info or {}  # type: ignore[union-attr]
    except Exception as exc:
        logger.debug("stock_provider=info_error symbol=%s error=%s", symbol, exc)

    # ── Price history ─────────────────────────────────────────────────────
    closes = [float(c) for c in hist["Close"].tolist()]
    raw_dates = hist.index.tolist()

    ma50_ser  = _rolling_avg(closes, 50)
    ma200_ser = _rolling_avg(closes, 200)

    price_history = [
        PricePoint(
            date=f"{d.month}/{d.day}",
            price=round(closes[i], 2),
            ma50=round(ma50_ser[i], 2),
            ma200=round(ma200_ser[i], 2),
        )
        for i, d in enumerate(raw_dates)
    ]

    current_price = round(closes[-1], 2)
    ma50  = round(ma50_ser[-1], 2)
    ma200 = round(ma200_ser[-1], 2)
    rsi   = _wilder_rsi(closes)
    support, resistance = _support_resistance(closes)

    if ma50 > ma200 and rsi > 50:
        trend = "Bullish"
    elif ma50 < ma200 and rsi < 50:
        trend = "Bearish"
    else:
        trend = "Neutral"

    # ── Company metadata ──────────────────────────────────────────────────
    name   = info.get("shortName") or info.get("longName") or symbol.upper()
    sector = info.get("sector") or info.get("industryDisp") or "—"

    # ── Ratios ────────────────────────────────────────────────────────────
    pe    = round(_nan_safe(info.get("trailingPE") or info.get("forwardPE")), 1)
    eps   = round(_nan_safe(info.get("epsTrailingTwelveMonths")), 2)

    roe_raw = _nan_safe(info.get("returnOnEquity"))
    # yfinance returnOnEquity is a decimal (0.46 = 46%)
    roe = round(roe_raw * 100, 1) if abs(roe_raw) <= 5 else round(roe_raw, 1)

    de_raw = _nan_safe(info.get("debtToEquity"))
    # yfinance sometimes returns as pct (e.g. 44.0 meaning 0.44x) — normalise
    de = round(de_raw / 100, 2) if de_raw > 20 else round(de_raw, 2)

    mkt_cap = _nan_safe(info.get("marketCap"))
    mkt_cap_str = _format_market_cap(mkt_cap, currency) if mkt_cap else "—"

    div_raw = _nan_safe(info.get("dividendYield") or info.get("trailingAnnualDividendYield"))
    # yfinance dividend yield is a decimal (0.018 = 1.8%)
    div_yield = round(div_raw * 100, 2) if div_raw < 1 else round(div_raw, 2)

    # ── Annual financials ─────────────────────────────────────────────────
    revenue_rows: List[RevenueEntry] = []
    profit_rows:  List[RevenueEntry] = []
    revenue_growth = 0.0
    profit_growth  = 0.0
    divisor = 1e7 if currency == "INR" else 1e9  # → Crore (INR) or Billion (USD)

    try:
        fin = ticker_obj.financials  # type: ignore[union-attr]
        if fin is not None and not fin.empty:
            cols = list(fin.columns[:3])
            cols.reverse()  # oldest first
            rev_key  = next((k for k in fin.index if "Total Revenue" in str(k)), None)
            prof_key = next((k for k in fin.index if "Net Income" in str(k)), None)

            for col in cols:
                fy = f"FY{str(col.year)[2:]}"
                if rev_key:
                    v = _nan_safe(fin.at[rev_key, col])
                    if v:
                        revenue_rows.append(RevenueEntry(year=fy, value=round(v / divisor, 1)))
                if prof_key:
                    v = _nan_safe(fin.at[prof_key, col])
                    if v:
                        profit_rows.append(RevenueEntry(year=fy, value=round(v / divisor, 1)))

            if len(revenue_rows) >= 2 and revenue_rows[-2].value:
                revenue_growth = round(
                    (revenue_rows[-1].value - revenue_rows[-2].value)
                    / abs(revenue_rows[-2].value) * 100, 1
                )
            if len(profit_rows) >= 2 and profit_rows[-2].value:
                profit_growth = round(
                    (profit_rows[-1].value - profit_rows[-2].value)
                    / abs(profit_rows[-2].value) * 100, 1
                )
    except Exception as exc:
        logger.warning("stock_provider=financials_error symbol=%s error=%s", symbol, exc)

    # ── Balance sheet ─────────────────────────────────────────────────────
    total_debt_val = 0.0
    cash_val       = 0.0
    try:
        bs = ticker_obj.balance_sheet  # type: ignore[union-attr]
        if bs is not None and not bs.empty:
            col0 = bs.columns[0]
            debt_key = next(
                (k for k in bs.index if "Total Debt" in str(k)), None
            )
            cash_key = next(
                (k for k in bs.index
                 if "Cash And Cash Equivalents" in str(k) or str(k) == "Cash"),
                None,
            )
            if debt_key:
                total_debt_val = _nan_safe(bs.at[debt_key, col0])
            if cash_key:
                cash_val = _nan_safe(bs.at[cash_key, col0])
    except Exception as exc:
        logger.warning("stock_provider=balance_error symbol=%s error=%s", symbol, exc)

    health_score, health_label = _health_score_and_label(cash_val, total_debt_val, de)
    total_debt_str = _format_value(total_debt_val, currency) if total_debt_val else "—"
    cash_str       = _format_value(cash_val, currency) if cash_val else "—"

    # ── Promoter / insider holding ─────────────────────────────────────────
    insider_pct = round(_nan_safe(info.get("heldPercentInsiders")) * 100, 1)

    # ── Rule-based pros / cons ─────────────────────────────────────────────
    pros: List[str] = []
    cons: List[str] = []

    if roe > 20:
        pros.append(f"High return on equity ({roe:.1f}%)")
    elif 0 < roe < 10:
        cons.append(f"Weak return on equity ({roe:.1f}%)")

    if de < 0.4:
        pros.append("Conservative balance sheet — low leverage")
    elif de > 1.2:
        cons.append(f"Elevated leverage (D/E {de:.2f}x)")

    if revenue_growth > 8:
        pros.append(f"Strong revenue growth ({revenue_growth:.1f}% YoY)")
    elif revenue_growth < 0:
        cons.append(f"Revenue declining ({revenue_growth:.1f}% YoY)")

    if profit_growth > 10:
        pros.append(f"Expanding profitability (+{profit_growth:.1f}% net income)")
    elif profit_growth < -5:
        cons.append(f"Profit under pressure ({profit_growth:.1f}%)")

    if div_yield > 2:
        pros.append(f"Attractive dividend yield ({div_yield:.1f}%)")

    if 0 < pe < 15:
        pros.append(f"Attractively valued at {pe:.1f}x P/E")
    elif pe > 40:
        cons.append(f"Stretched valuation ({pe:.1f}x P/E)")

    if ma50 > ma200:
        pros.append("Golden cross active — MA50 above MA200 (bullish)")
    else:
        cons.append("MA50 below MA200 — bearish technical structure")

    if rsi < 35:
        pros.append(f"Oversold (RSI {rsi}) — potential mean-reversion opportunity")
    elif rsi > 70:
        cons.append(f"Overbought (RSI {rsi}) — elevated short-term correction risk")

    if not pros:
        pros = ["Review latest filings for qualitative investment thesis"]
    if not cons:
        cons = ["No major risk flags identified from available data"]

    logger.info(
        "stock_provider=ok symbol=%s currency=%s price=%.2f rsi=%.1f trend=%s",
        symbol, currency, current_price, rsi, trend,
    )

    return StockDetailResponse(
        symbol=symbol.upper(),
        name=name,
        sector=sector,
        currency=currency,
        competitors=[],  # yfinance has no peer list endpoint
        revenue=revenue_rows,
        profit=profit_rows,
        revenueGrowth=revenue_growth,
        profitGrowth=profit_growth,
        balance=StockBalanceResponse(
            totalDebt=total_debt_str,
            cash=cash_str,
            healthScore=health_score,
            healthLabel=health_label,
        ),
        promoterHolding=insider_pct,
        pros=pros[:5],
        cons=cons[:4],
        ratios=StockRatiosResponse(
            pe=pe,
            eps=eps,
            roe=roe,
            debtToEquity=de,
            marketCap=mkt_cap_str,
            dividendYield=div_yield,
        ),
        technical=StockTechnicalResponse(
            rsi=rsi,
            trend=trend,
            ma50=ma50,
            ma200=ma200,
            currentPrice=current_price,
            support=support,
            resistance=resistance,
            fibonacci=_fib_levels(support, resistance),
            priceHistory=price_history,
        ),
    )


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------

async def get_stock_detail(symbol: str) -> Optional[StockDetailResponse]:
    """Fetch rich stock detail. Returns None if symbol has no data."""
    cache_key = f"detail:{symbol.upper()}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached  # type: ignore[return-value]

    loop = asyncio.get_event_loop()
    result: Optional[StockDetailResponse] = None
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _fetch_sync, symbol),
            timeout=_YF_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.warning("stock_provider=timeout symbol=%s", symbol)
    except Exception as exc:
        logger.warning("stock_provider=error symbol=%s error=%s", symbol, exc)

    if result is not None:
        _cache.set(cache_key, result, _DETAIL_CACHE_TTL)
    return result
