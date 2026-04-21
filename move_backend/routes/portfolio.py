from fastapi import APIRouter, HTTPException, Query

from core.exceptions import PipelineError
from models.schemas import PortfolioResponse
from services.orchestrator import run_portfolio_summary

router = APIRouter(tags=["portfolio"])

_DEFAULT_DATE = "2026-04-20"


@router.get("/portfolio-summary", response_model=PortfolioResponse)
async def portfolio_summary(
    date: str = Query(default=_DEFAULT_DATE, description="ISO date YYYY-MM-DD"),
) -> PortfolioResponse:
    try:
        return await run_portfolio_summary(date)
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
