from fastapi import APIRouter, HTTPException, Query

from core.exceptions import PipelineError
from models.schemas import WhyCardResponse
from services.orchestrator import run_why_card

router = APIRouter(tags=["why-card"])

_DEFAULT_DATE = "2026-04-20"


@router.get("/daily-why-card", response_model=WhyCardResponse)
async def daily_why_card(
    date: str = Query(default=_DEFAULT_DATE, description="ISO date YYYY-MM-DD"),
) -> WhyCardResponse:
    try:
        return await run_why_card(date)
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
