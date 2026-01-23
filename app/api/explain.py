"""
FastAPI endpoint for /explain
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.market_data import MarketDataService
from app.services.news_service import NewsService
from app.services.ai_engine import AIEngine

router = APIRouter()

class ExplainRequest(BaseModel):
    symbol: str
    date: str

@router.post("/explain")
def explain(req: ExplainRequest):
    market = MarketDataService()
    news = NewsService()
    ai = AIEngine()

    # Fetch market data
    daily = market.fetch_daily_data(req.symbol, req.date)
    if not daily:
        raise HTTPException(404, detail="No market data found for this symbol/date.")
    avg_vol = market.fetch_20d_avg_volume(req.symbol, req.date)
    if not avg_vol:
        raise HTTPException(404, detail="Not enough volume data.")
    volume_ratio = round(daily['volume'] / avg_vol, 2) if avg_vol else 0
    # Index and sector
    index_close = market.fetch_index_performance(req.date)
    sector_close = market.fetch_sector_performance("XLK", req.date)  # Example: tech ETF
    # Compute % changes
    price_change = round((daily['close'] - daily['open']) / daily['open'] * 100, 2)
    index_change = 0.0
    sector_change = 0.0
    # News
    headlines = news.fetch_headlines(req.symbol, req.date)
    # Evidence block
    evidence = {
        "symbol": req.symbol,
        "date": req.date,
        "price_change": price_change,
        "volume": daily['volume'],
        "volume_ratio": volume_ratio,
        "index_change": index_change,
        "sector_change": sector_change,
        "headlines": headlines
    }
    # AI explanation
    ai_result = ai.explain(evidence)
    if "error" in ai_result:
        raise HTTPException(500, detail=ai_result["error"])
    return {
        "symbol": req.symbol,
        "date": req.date,
        "price_change": price_change,
        "volume": daily['volume'],
        "volume_ratio": volume_ratio,
        "index_change": index_change,
        "sector_change": sector_change,
        "headlines": headlines,
        "explanation": ai_result["explanation"]
    }
