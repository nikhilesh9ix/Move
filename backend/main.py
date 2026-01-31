"""
FastAPI application for AI Stock Movement Explainer.
Main API endpoint: POST /explain
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ExplainRequest, ExplainResponse, ErrorResponse
from services.market_data import market_data_service
from services.news_service import news_service
from services.evidence_builder import evidence_builder
from services.ai_engine import ai_engine
import logging
from demo import router as demo_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Stock Movement Explainer",
    description="Explains why stocks moved on specific dates using AI-powered causal analysis",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include demo router
app.include_router(demo_router, tags=["demo"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AI Stock Movement Explainer",
        "version": "1.0.0",
        "demo": "Use POST /demo/explain to see a working demo (no input required)",
    }


@app.post("/explain", response_model=ExplainResponse)
async def explain_movement(request: ExplainRequest):
    """
    Explain why a stock moved on a specific date with enhanced analysis.

    Args:
        request: ExplainRequest with symbol, date, and analysis options

    Returns:
        ExplainResponse with detailed explanation and enhanced features

    Raises:
        HTTPException: If data cannot be fetched or processed
    """
    try:
        logger.info(f"Processing request for {request.symbol} on {request.date}")

        # Step 1: Fetch market data
        try:
            market_data = market_data_service.get_stock_data(
                request.symbol, request.date
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching market data: {str(e)}"
            )

        # Step 2: Fetch news with sentiment
        news_items = news_service.get_news_with_sentiment(request.symbol, request.date)

        # Step 3: Build evidence
        evidence = evidence_builder.build_evidence(market_data, news_items)

        logger.info(f"Evidence compiled for {request.symbol}")

        # Step 4: Generate AI explanation
        try:
            explanation = ai_engine.generate_explanation(
                evidence=evidence,
                symbol=request.symbol,
                date=request.date,
                price_change_percent=market_data["price_change_percent"],
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating explanation: {str(e)}"
            )

        # Step 5: Fetch enhanced data based on request flags
        historical_data = None
        if request.include_historical:
            try:
                hist_data = market_data_service.get_historical_data(
                    request.symbol, request.date, request.days_range or 30
                )
                historical_data = [
                    {
                        "date": d["date"],
                        "open": d["open"],
                        "high": d["high"],
                        "low": d["low"],
                        "close": d["close"],
                        "volume": d["volume"],
                        "ma_20": d.get("ma_20"),
                        "ma_50": d.get("ma_50"),
                    }
                    for d in hist_data
                ]
            except Exception as e:
                logger.warning(f"Could not fetch historical data: {str(e)}")

        sector_context = None
        if request.include_sector_analysis:
            try:
                sector_context = market_data_service.get_sector_context(
                    request.symbol, request.date
                )
            except Exception as e:
                logger.warning(f"Could not fetch sector context: {str(e)}")

        technical_indicators = None
        try:
            technical_indicators = market_data_service.get_technical_indicators(
                request.symbol, request.date
            )
        except Exception as e:
            logger.warning(f"Could not calculate technical indicators: {str(e)}")

        multi_day_pattern = None
        try:
            multi_day_pattern = market_data_service.analyze_multi_day_pattern(
                request.symbol, request.date, days=7
            )
        except Exception as e:
            logger.warning(f"Could not analyze multi-day pattern: {str(e)}")

        # Step 6: Build enhanced response
        response = ExplainResponse(
            symbol=request.symbol,
            date=request.date,
            price_change_percent=market_data["price_change_percent"],
            explanation=explanation["full_explanation"],
            primary_driver=explanation["primary_driver"],
            supporting_factors=explanation["supporting_factors"],
            move_classification=explanation["move_classification"],
            confidence_score=explanation["confidence_score"],
            uncertainty_note=explanation.get("uncertainty_note"),
            historical_data=historical_data,
            sector_context=sector_context,
            news_with_sentiment=news_items if request.include_sentiment else None,
            technical_indicators=technical_indicators,
            multi_day_pattern=multi_day_pattern,
        )

        logger.info(f"Successfully generated enhanced explanation for {request.symbol}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "market_data": "operational",
            "news": "operational",
            "ai_engine": "operational",
        },
    }


@app.get("/historical/{symbol}")
async def get_historical_data(symbol: str, end_date: str, days: int = 30):
    """
    Get historical price data with technical indicators.
    
    Args:
        symbol: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        days: Number of days of history (default 30, max 365)
        
    Returns:
        List of historical data points
    """
    try:
        if days > 365:
            raise HTTPException(status_code=400, detail="Maximum 365 days allowed")
        
        hist_data = market_data_service.get_historical_data(symbol, end_date, days)
        return {"symbol": symbol, "data": hist_data}
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news-timeline/{symbol}")
async def get_news_timeline(symbol: str, end_date: str, days: int = 7):
    """
    Get news timeline over multiple days.
    
    Args:
        symbol: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        days: Number of days to look back (default 7, max 30)
        
    Returns:
        Chronologically ordered news with sentiment
    """
    try:
        if days > 30:
            raise HTTPException(status_code=400, detail="Maximum 30 days allowed")
        
        timeline = news_service.get_news_timeline(symbol, end_date, days)
        return {"symbol": symbol, "timeline": timeline}
    except Exception as e:
        logger.error(f"Error fetching news timeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sector-context/{symbol}")
async def get_sector_analysis(symbol: str, date: str):
    """
    Get comprehensive sector and market context.
    
    Args:
        symbol: Stock ticker symbol
        date: Date in YYYY-MM-DD format
        
    Returns:
        Sector context with market indices and peer comparison
    """
    try:
        sector_context = market_data_service.get_sector_context(symbol, date)
        if not sector_context:
            raise HTTPException(status_code=404, detail="Sector context not available")
        return sector_context
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sector context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare")
async def compare_stocks(symbols: str, date: str):
    """
    Compare multiple stocks on the same date.
    
    Args:
        symbols: Comma-separated stock symbols (e.g., "AAPL,MSFT,GOOGL")
        date: Date in YYYY-MM-DD format
        
    Returns:
        Comparison data for all stocks
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        if len(symbol_list) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 stocks allowed")
        
        comparisons = []
        for symbol in symbol_list:
            try:
                data = market_data_service.get_stock_data(symbol, date)
                comparisons.append({
                    "symbol": symbol,
                    "price_change_percent": data["price_change_percent"],
                    "volume_ratio": data.get("volume_ratio", 1.0),
                    "sector": data.get("sector_info", {}).get("sector", "Unknown"),
                })
            except Exception as e:
                logger.warning(f"Could not fetch data for {symbol}: {str(e)}")
                continue
        
        return {"date": date, "stocks": comparisons}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
