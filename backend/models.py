"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class ExplainRequest(BaseModel):
    """Request model for stock movement explanation."""

    symbol: str = Field(
        ..., description="Stock ticker symbol (e.g., AAPL)", min_length=1, max_length=10
    )
    date: str = Field(
        ..., description="Date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    include_historical: bool = Field(
        default=True, description="Include historical price chart data"
    )
    include_sector_analysis: bool = Field(
        default=True, description="Include sector and market context"
    )
    include_sentiment: bool = Field(
        default=True, description="Include sentiment analysis on news"
    )
    days_range: Optional[int] = Field(
        default=30, description="Number of days for historical analysis", ge=1, le=365
    )


class HistoricalDataPoint(BaseModel):
    """Single point in historical price data."""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    ma_20: Optional[float] = None
    ma_50: Optional[float] = None


class NewsWithSentiment(BaseModel):
    """News article with sentiment analysis."""
    title: str
    source: str
    published_at: str
    description: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # positive, negative, neutral
    credibility_score: float  # 0 to 1
    price_impact: Optional[float] = None


class SectorContext(BaseModel):
    """Sector and market context analysis."""
    sector_name: str
    sector_change_percent: float
    sp500_change_percent: float
    nasdaq_change_percent: float
    relative_strength: float  # stock vs sector
    correlation_with_sector: Optional[float] = None
    peer_stocks: Optional[List[Dict[str, Any]]] = None


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators."""
    ma_20: Optional[float] = None
    ma_50: Optional[float] = None
    rsi: Optional[float] = None
    volume_avg_20d: Optional[int] = None
    volume_ratio: Optional[float] = None


class MultiDayPattern(BaseModel):
    """Multi-day movement pattern."""
    pattern_type: str
    start_date: str
    end_date: str
    cumulative_change: float
    description: str
    similar_historical_events: Optional[List[str]] = None


class ExplainResponse(BaseModel):
    """Response model for stock movement explanation."""

    symbol: str
    date: str
    price_change_percent: float
    explanation: str
    primary_driver: str
    supporting_factors: List[str]
    move_classification: str
    confidence_score: float
    uncertainty_note: Optional[str] = None
    
    # New enhanced features
    historical_data: Optional[List[HistoricalDataPoint]] = None
    sector_context: Optional[SectorContext] = None
    news_with_sentiment: Optional[List[NewsWithSentiment]] = None
    technical_indicators: Optional[TechnicalIndicators] = None
    multi_day_pattern: Optional[MultiDayPattern] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
