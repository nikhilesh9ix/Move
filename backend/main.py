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
    Explain why a stock moved on a specific date.

    Args:
        request: ExplainRequest with symbol and date

    Returns:
        ExplainResponse with detailed explanation

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

        # Step 2: Fetch news
        news_items = news_service.get_news(request.symbol, request.date)

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

        # Step 5: Build response
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
        )

        logger.info(f"Successfully generated explanation for {request.symbol}")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
