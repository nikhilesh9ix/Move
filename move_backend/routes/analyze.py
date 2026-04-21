from fastapi import APIRouter, HTTPException

from core.exceptions import PipelineError
from models.schemas import AnalyzeRequest, AnalyzeResponse
from services.orchestrator import run_analysis

router = APIRouter(tags=["analysis"])


@router.post("/analyze-move", response_model=AnalyzeResponse)
async def analyze_move(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return await run_analysis(request.stock, request.date)
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
