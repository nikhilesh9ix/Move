"""
FastAPI Application
REST API for the "Why Did This Move?" Engine
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from src.move_engine import MoveEngine

# Initialize FastAPI app
app = FastAPI(
    title="Why Did This Move? API",
    description="AI-powered financial intelligence system that explains stock movements",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the move engine
move_engine = MoveEngine()


# Request/Response Models
class ExplainRequest(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    market_index: Optional[str] = Field("^GSPC", description="Market index for comparison")
    include_raw_data: Optional[bool] = Field(False, description="Include raw analysis data")


class QuickCheckRequest(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: str = Field(..., description="Date in YYYY-MM-DD format")


class BatchAnalyzeRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols")
    date: str = Field(..., description="Date in YYYY-MM-DD format")


class TopMoversRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols to check")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    top_n: Optional[int] = Field(5, description="Number of top movers to return")


# Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Why Did This Move? API",
        "version": "1.0.0",
        "description": "Explains stock movements using AI-powered analysis",
        "endpoints": {
            "explain": "/explain - Generate full explanation for a stock movement",
            "quick_check": "/quick-check - Quick check if movement is significant",
            "batch_analyze": "/batch-analyze - Analyze multiple stocks",
            "top_movers": "/top-movers - Find and explain top movers",
            "health": "/health - API health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/explain")
async def explain_move(request: ExplainRequest):
    """
    Generate a comprehensive explanation for why a stock moved on a specific day.
    
    Returns detailed analysis including:
    - Primary driver of the movement
    - Supporting factors
    - Market context
    - News headlines
    - Confidence score
    """
    try:
        # Validate date format
        datetime.strptime(request.date, "%Y-%m-%d")
        
        explanation = move_engine.explain_move(
            symbol=request.symbol.upper(),
            date=request.date,
            market_index=request.market_index,
            include_raw_data=request.include_raw_data
        )
        
        return explanation
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/quick-check")
async def quick_check(request: QuickCheckRequest):
    """
    Quick check to see if a stock had significant movement on a date.
    
    Useful for filtering before requesting full explanations.
    """
    try:
        datetime.strptime(request.date, "%Y-%m-%d")
        
        result = move_engine.quick_check(
            symbol=request.symbol.upper(),
            date=request.date
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check failed: {str(e)}")


@app.post("/batch-analyze")
async def batch_analyze(request: BatchAnalyzeRequest):
    """
    Analyze multiple stocks for the same date.
    
    Returns explanations for all requested symbols.
    """
    try:
        datetime.strptime(request.date, "%Y-%m-%d")
        
        if len(request.symbols) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 symbols allowed per batch request"
            )
        
        results = move_engine.batch_analyze(
            symbols=[s.upper() for s in request.symbols],
            date=request.date
        )
        
        return results
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.post("/top-movers")
async def top_movers(request: TopMoversRequest):
    """
    Identify and explain the top movers from a list of stocks.
    
    Useful for getting insights on the most significant movements.
    """
    try:
        datetime.strptime(request.date, "%Y-%m-%d")
        
        if len(request.symbols) > 50:
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 symbols allowed for top movers analysis"
            )
        
        movers = move_engine.get_top_movers(
            symbols=[s.upper() for s in request.symbols],
            date=request.date,
            top_n=request.top_n
        )
        
        return {
            "date": request.date,
            "total_checked": len(request.symbols),
            "top_movers_count": len(movers),
            "movers": movers
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Top movers analysis failed: {str(e)}")


@app.get("/symbols/popular")
async def popular_symbols():
    """
    Get a list of popular stock symbols for testing.
    """
    return {
        "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
        "finance": ["JPM", "BAC", "WFC", "GS", "MS"],
        "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "TMO"],
        "energy": ["XOM", "CVX", "COP", "SLB"],
        "consumer": ["WMT", "PG", "KO", "PEP", "NKE"],
        "indices": {
            "sp500": "^GSPC",
            "nasdaq": "^IXIC",
            "dow": "^DJI"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)
