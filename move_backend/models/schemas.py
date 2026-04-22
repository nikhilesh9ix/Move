from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# API request / response contracts (public surface)
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    stock: str = Field(..., min_length=1, max_length=20)
    date: str = Field(..., description="ISO date: YYYY-MM-DD")

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("date must be YYYY-MM-DD")
        return v

    @field_validator("stock")
    @classmethod
    def normalize_stock(cls, v: str) -> str:
        return v.strip().upper()


class Attribution(BaseModel):
    factor: str
    contribution: float = Field(..., ge=0.0, le=100.0)


class AnalyzeResponse(BaseModel):
    stock: str
    price_change: float
    attribution: List[Attribution]
    explanation: str
    historical_hint: str = ""
    actionable_insight: str = ""
    confidence_pct: int = Field(default=70, ge=0, le=100)


class HoldingChange(BaseModel):
    stock: str
    price_change: float
    value_change: float


class PortfolioResponse(BaseModel):
    total_value: float
    total_change_pct: float
    top_gainers: List[HoldingChange]
    top_losers: List[HoldingChange]


class CauseItem(BaseModel):
    cause: str
    impact: float


class WhyCardResponse(BaseModel):
    date: str
    total_portfolio_change_pct: float
    top_causes: List[CauseItem]
    explanation_summary: str
    confidence_pct: int = Field(default=70, ge=0, le=100)
    confidence_label: str = "Medium"
    primary_driver_label: str = ""


# ---------------------------------------------------------------------------
# Internal pipeline transfer models (agent inputs / outputs)
# ---------------------------------------------------------------------------


class MarketDataQuery(BaseModel):
    """Input contract for MarketDataAgent."""

    stock: str
    date: str


class PriceData(BaseModel):
    """Typed output from MarketDataAgent. Replaces raw dict between agents."""

    stock: str
    date: str
    price_change: float
    base_price: float
    volatility: float
    volume: int
    direction: str        # "up" | "down"
    source: str = "mock"  # "yfinance" | "mock"


class AttributionResult(BaseModel):
    """Typed output from CausalInferenceAgent."""

    items: List[Attribution]

    def dominant(self) -> Attribution:
        return max(self.items, key=lambda a: a.contribution)


class ExplanationInput(BaseModel):
    """Input contract for ExplanationAgent."""

    stock: str
    attribution: AttributionResult
    price_change: float = 0.0  # direction-aware templates need sign


class ExplanationResult(BaseModel):
    """Typed output from ExplanationAgent."""

    text: str
    dominant_factor: str
    historical_hint: str = ""
    actionable_insight: str = ""
    confidence_pct: int = Field(default=70, ge=0, le=100)
    confidence_label: str = "Medium"


# ---------------------------------------------------------------------------
# Stock detail response models (GET /stock/{symbol})
# ---------------------------------------------------------------------------


class FibLevel(BaseModel):
    level: str
    value: float


class PricePoint(BaseModel):
    date: str
    price: float
    ma50: float
    ma200: float


class RevenueEntry(BaseModel):
    year: str
    value: float


class StockBalanceResponse(BaseModel):
    totalDebt: str
    cash: str
    healthScore: int
    healthLabel: str  # 'Strong' | 'Moderate' | 'Weak'


class StockRatiosResponse(BaseModel):
    pe: float
    eps: float
    roe: float
    debtToEquity: float
    marketCap: str
    dividendYield: float


class StockTechnicalResponse(BaseModel):
    rsi: float
    trend: str  # 'Bullish' | 'Bearish' | 'Neutral'
    ma50: float
    ma200: float
    currentPrice: float
    support: float
    resistance: float
    fibonacci: List[FibLevel]
    priceHistory: List[PricePoint]


class StockDetailResponse(BaseModel):
    symbol: str
    name: str
    sector: str
    currency: str           # 'INR' | 'USD'
    competitors: List[str]
    revenue: List[RevenueEntry]
    profit: List[RevenueEntry]
    revenueGrowth: float
    profitGrowth: float
    balance: StockBalanceResponse
    promoterHolding: float  # 0–100 %
    pros: List[str]
    cons: List[str]
    ratios: StockRatiosResponse
    technical: StockTechnicalResponse


# ---------------------------------------------------------------------------
# Internal pipeline models
# ---------------------------------------------------------------------------


class NewsSignal(BaseModel):
    """Latest news item for a stock, with pre-computed sentiment."""

    stock: str
    headline: str
    sentiment: float            # −1.0 (very negative) → +1.0 (very positive)
    source: str = "yfinance"
    url: str = ""
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CausalInferenceInput(BaseModel):
    """Input contract for CausalInferenceAgent (price + optional news signal)."""

    price_data: PriceData
    news_signal: Optional[NewsSignal] = None
