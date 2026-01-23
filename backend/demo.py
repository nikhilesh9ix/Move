"""
Demo endpoint with mock data to demonstrate the application when Yahoo Finance is rate-limited.
"""

from fastapi import APIRouter
from models import ExplainResponse
from typing import List

router = APIRouter()


@router.post("/demo/explain", response_model=ExplainResponse)
async def demo_explain():
    """
    Demo endpoint with pre-generated mock data to show the application working.
    Use this when Yahoo Finance is rate-limited.
    """
    return ExplainResponse(
        symbol="AAPL",
        date="2024-11-01",
        price_change_percent=2.81,
        explanation="""SUMMARY:
Apple (AAPL) rose 2.81% on November 1, 2024, driven primarily by strong iPhone 16 sales momentum and positive analyst sentiment following the company's better-than-expected Q4 earnings report released the previous week. The move was stock-specific, supported by sector strength in technology.

PRIMARY DRIVER:
Continued strong demand for iPhone 16 series, particularly the Pro models, with supply chain reports indicating production increases to meet higher-than-anticipated consumer demand during the holiday shopping season kickoff.

SUPPORTING FACTORS:
- Technology sector (XLK) gained 1.8% on the same day, providing tailwind
- Analyst upgrades from major firms citing AI integration in Apple products
- Services revenue growth trajectory exceeding expectations
- Market anticipation of holiday quarter guidance

MOVE CLASSIFICATION:
MIXED

CONFIDENCE SCORE:
0.82

UNCERTAINTY NOTE:
While the primary drivers are clear, the exact weight of each factor is difficult to isolate. The broader tech sector strength suggests some market-driven component alongside stock-specific catalysts.""",
        primary_driver="Continued strong demand for iPhone 16 series, particularly the Pro models, with supply chain reports indicating production increases to meet higher-than-anticipated consumer demand during the holiday shopping season kickoff.",
        supporting_factors=[
            "Technology sector (XLK) gained 1.8% on the same day, providing tailwind",
            "Analyst upgrades from major firms citing AI integration in Apple products",
            "Services revenue growth trajectory exceeding expectations",
            "Market anticipation of holiday quarter guidance",
        ],
        move_classification="MIXED",
        confidence_score=0.82,
        uncertainty_note="While the primary drivers are clear, the exact weight of each factor is difficult to isolate. The broader tech sector strength suggests some market-driven component alongside stock-specific catalysts.",
    )
