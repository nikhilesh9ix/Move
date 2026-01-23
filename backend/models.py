"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ExplainRequest(BaseModel):
    """Request model for stock movement explanation."""

    symbol: str = Field(
        ..., description="Stock ticker symbol (e.g., AAPL)", min_length=1, max_length=10
    )
    date: str = Field(
        ..., description="Date in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"
    )


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


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
