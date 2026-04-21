from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

from agents.causal_inference_agent import CausalInferenceAgent
from agents.explanation_agent import ExplanationAgent
from agents.market_data_agent import MarketDataAgent
from core.exceptions import AgentError, PipelineError
from core.logging import get_logger
from data.news_provider import get_news_signal
from models.schemas import (
    AnalyzeResponse,
    CausalInferenceInput,
    CauseItem,
    ExplanationInput,
    HoldingChange,
    MarketDataQuery,
    NewsSignal,
    PortfolioResponse,
    PriceData,
    WhyCardResponse,
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Agent singletons — instantiated once, reused across all requests
# ---------------------------------------------------------------------------
_market_agent = MarketDataAgent()
_causal_agent = CausalInferenceAgent()
_explanation_agent = ExplanationAgent()

# ---------------------------------------------------------------------------
# Mock portfolio
# ---------------------------------------------------------------------------
_PORTFOLIO: List[Dict[str, object]] = [
    {"stock": "TCS",      "shares": 10, "avg_cost": 3500.0},
    {"stock": "INFY",     "shares": 25, "avg_cost": 1500.0},
    {"stock": "RELIANCE", "shares":  5, "avg_cost": 2800.0},
    {"stock": "HDFC",     "shares":  8, "avg_cost": 1600.0},
    {"stock": "WIPRO",    "shares": 30, "avg_cost":  450.0},
]


# ---------------------------------------------------------------------------
# Pipeline helpers
# ---------------------------------------------------------------------------

async def _fetch_price(stock: str, date: str) -> PriceData:
    try:
        return await _market_agent.run(MarketDataQuery(stock=stock, date=date))
    except Exception as exc:
        raise AgentError(_market_agent.name, str(exc)) from exc


async def _fetch_news(stock: str) -> Optional[NewsSignal]:
    try:
        return await get_news_signal(stock)
    except Exception as exc:
        logger.warning("pipeline=news_fetch_error stock=%s error=%s", stock, exc)
        return None


async def _compute_attribution(
    price_data: PriceData,
    news_signal: Optional[NewsSignal] = None,
):
    try:
        return await _causal_agent.run(
            CausalInferenceInput(price_data=price_data, news_signal=news_signal)
        )
    except Exception as exc:
        raise AgentError(_causal_agent.name, str(exc)) from exc


async def _generate_explanation(stock: str, attribution, price_change: float = 0.0):
    try:
        return await _explanation_agent.run(
            ExplanationInput(stock=stock, attribution=attribution, price_change=price_change)
        )
    except Exception as exc:
        raise AgentError(_explanation_agent.name, str(exc)) from exc


# ---------------------------------------------------------------------------
# Public pipeline: single stock
# ---------------------------------------------------------------------------

async def run_analysis(stock: str, analysis_date: str) -> AnalyzeResponse:
    logger.info("pipeline=analyze_start stock=%s date=%s", stock, analysis_date)
    try:
        price_data, news_signal = await asyncio.gather(
            _fetch_price(stock, analysis_date),
            _fetch_news(stock),
        )
        attribution = await _compute_attribution(price_data, news_signal)
        expl = await _generate_explanation(stock, attribution, price_data.price_change)

        logger.info("pipeline=analyze_complete stock=%s confidence=%d%%", stock, expl.confidence_pct)
        return AnalyzeResponse(
            stock=price_data.stock,
            price_change=price_data.price_change,
            attribution=attribution.items,
            explanation=expl.text,
            historical_hint=expl.historical_hint,
            actionable_insight=expl.actionable_insight,
            confidence_pct=expl.confidence_pct,
        )
    except AgentError as exc:
        logger.error("pipeline=analyze_failed stock=%s agent=%s reason=%s", stock, exc.agent_name, exc.reason)
        raise PipelineError(stage=exc.agent_name, reason=exc.reason) from exc
    except Exception as exc:
        logger.exception("pipeline=analyze_unexpected_error stock=%s", stock)
        raise PipelineError(stage="unknown", reason=str(exc)) from exc


# ---------------------------------------------------------------------------
# Public pipeline: portfolio summary
# ---------------------------------------------------------------------------

async def run_portfolio_summary(summary_date: str) -> PortfolioResponse:
    logger.info("pipeline=portfolio_start date=%s holdings=%d", summary_date, len(_PORTFOLIO))
    try:
        # Fetch all prices in parallel — avoids sequential 3-4s yfinance timeouts per holding
        price_results = await asyncio.gather(
            *[_fetch_price(str(h["stock"]), summary_date) for h in _PORTFOLIO],
            return_exceptions=True,
        )

        holding_changes: List[HoldingChange] = []
        total_start_value = 0.0
        total_end_value = 0.0

        for holding, price_result in zip(_PORTFOLIO, price_results):
            stock    = str(holding["stock"])
            shares   = float(holding["shares"])    # type: ignore[arg-type]
            avg_cost = float(holding["avg_cost"])  # type: ignore[arg-type]

            if isinstance(price_result, Exception):
                logger.warning("pipeline=price_fetch_failed stock=%s error=%s", stock, price_result)
                continue

            price_data = price_result
            start_value = avg_cost * shares
            end_value   = start_value * (1 + price_data.price_change / 100)
            value_change = end_value - start_value

            total_start_value += start_value
            total_end_value   += end_value

            holding_changes.append(
                HoldingChange(
                    stock=stock,
                    price_change=price_data.price_change,
                    value_change=round(value_change, 2),
                )
            )

        if total_start_value == 0:
            raise PipelineError(stage="portfolio_summary", reason="All price fetches failed")

        total_change_pct = round(
            (total_end_value - total_start_value) / total_start_value * 100, 2
        )
        by_change = sorted(holding_changes, key=lambda h: h.price_change)

        logger.info("pipeline=portfolio_complete date=%s total_change_pct=%.2f", summary_date, total_change_pct)
        return PortfolioResponse(
            total_value=round(total_end_value, 2),
            total_change_pct=total_change_pct,
            top_gainers=[h for h in reversed(by_change) if h.price_change > 0][:3],
            top_losers=[h for h in by_change if h.price_change < 0][:3],
        )
    except AgentError as exc:
        logger.error("pipeline=portfolio_failed agent=%s reason=%s", exc.agent_name, exc.reason)
        raise PipelineError(stage=exc.agent_name, reason=exc.reason) from exc
    except Exception as exc:
        logger.exception("pipeline=portfolio_unexpected_error date=%s", summary_date)
        raise PipelineError(stage="portfolio_summary", reason=str(exc)) from exc


# ---------------------------------------------------------------------------
# WhyCard helpers
# ---------------------------------------------------------------------------

_DRIVER_LABELS: Dict[str, str] = {
    "sector": "Sector-wide pressure",
    "macro": "Macro headwinds",
    "rates": "Rate sensitivity",
    "earnings": "Earnings revision",
    "idiosyncratic": "Company-specific news",
}

_PORTFOLIO_CONTEXT: Dict[str, str] = {
    "sector": (
        "Sector-wide dynamics are affecting {n} of your holdings simultaneously, "
        "creating correlated portfolio-level pressure."
    ),
    "macro": (
        "Macroeconomic forces drove broad-based moves across your portfolio — "
        "large-cap holdings were hit hardest."
    ),
    "rates": (
        "Interest rate sensitivity is creating correlated movement across your holdings, "
        "compressing growth-stock valuations."
    ),
    "earnings": (
        "Earnings expectations and analyst revisions are the primary mover across "
        "your portfolio today."
    ),
    "idiosyncratic": (
        "Company-specific events across multiple holdings contributed to the overall "
        "portfolio move independently of sector trends."
    ),
}

_PORTFOLIO_HISTORICAL: Dict[str, str] = {
    "sector": "Sector-driven portfolio moves historically normalise within 3–5 trading days.",
    "macro": "Macro headwinds affecting diversified portfolios typically persist 1–2 weeks.",
    "rates": "Rate-driven portfolio compression often reverses once rate expectations stabilise.",
    "earnings": "Earnings-revision cycles propagate across a portfolio over 1–3 weeks.",
    "idiosyncratic": "Company-specific events across holdings resolve on different timelines.",
}


def _portfolio_explanation(dominant: "CauseItem", change_pct: float, n_holdings: int) -> str:
    context_tpl = _PORTFOLIO_CONTEXT.get(
        dominant.cause,
        f"{dominant.cause.capitalize()} was the primary driver across your holdings.",
    )
    context = context_tpl.format(n=n_holdings)
    historical = _PORTFOLIO_HISTORICAL.get(dominant.cause, "")
    direction_word = "gain" if change_pct >= 0 else "decline"
    return (
        f"{context} {dominant.cause.capitalize()} accounted for "
        f"{dominant.impact:.0f}% of the total portfolio {direction_word}. {historical}"
    )


def _portfolio_confidence(top_causes: List["CauseItem"]) -> tuple:
    if not top_causes:
        return 60, "Medium"
    top_pct = top_causes[0].impact
    if top_pct >= 55:
        return min(91, int(75 + (top_pct - 55) * 0.8)), "High"
    if top_pct >= 35:
        return int(63 + (top_pct - 35) * 0.6), "Medium"
    return max(45, int(45 + top_pct * 0.5)), "Low"


# ---------------------------------------------------------------------------
# Public pipeline: daily why-card
# ---------------------------------------------------------------------------

async def run_why_card(card_date: str) -> WhyCardResponse:
    logger.info("pipeline=whycard_start date=%s", card_date)
    try:
        portfolio_summary = await run_portfolio_summary(card_date)

        # Prices cached from run_portfolio_summary call above; gather attribution in parallel
        factor_totals: Dict[str, float] = {}
        price_tasks = await asyncio.gather(
            *[_fetch_price(str(h["stock"]), card_date) for h in _PORTFOLIO],
            return_exceptions=True,
        )
        attribution_tasks = await asyncio.gather(
            *[
                _compute_attribution(p) if not isinstance(p, Exception) else asyncio.sleep(0)
                for p in price_tasks
            ],
            return_exceptions=True,
        )

        for holding, price_result, attr_result in zip(_PORTFOLIO, price_tasks, attribution_tasks):
            if isinstance(price_result, Exception) or isinstance(attr_result, Exception):
                continue
            if attr_result is None:  # from asyncio.sleep(0) fallback
                continue
            position_weight = float(holding["avg_cost"]) * float(holding["shares"])  # type: ignore[arg-type]
            for item in attr_result.items:
                factor_totals[item.factor] = (
                    factor_totals.get(item.factor, 0.0) + item.contribution * position_weight
                )

        grand_total = sum(factor_totals.values())
        top_causes: List[CauseItem] = sorted(
            [
                CauseItem(cause=factor, impact=round(weight / grand_total * 100, 1))
                for factor, weight in factor_totals.items()
            ],
            key=lambda c: c.impact,
            reverse=True,
        )[:3]

        dominant = top_causes[0] if top_causes else CauseItem(cause="unknown", impact=0.0)
        summary = _portfolio_explanation(dominant, portfolio_summary.total_change_pct, len(_PORTFOLIO))
        conf_pct, conf_label = _portfolio_confidence(top_causes)
        driver_label = _DRIVER_LABELS.get(dominant.cause, dominant.cause.capitalize())

        logger.info(
            "pipeline=whycard_complete date=%s dominant_cause=%s confidence=%d%%",
            card_date, dominant.cause, conf_pct,
        )
        return WhyCardResponse(
            date=card_date,
            total_portfolio_change_pct=portfolio_summary.total_change_pct,
            top_causes=top_causes,
            explanation_summary=summary,
            confidence_pct=conf_pct,
            confidence_label=conf_label,
            primary_driver_label=driver_label,
        )
    except PipelineError:
        raise
    except Exception as exc:
        logger.exception("pipeline=whycard_unexpected_error date=%s", card_date)
        raise PipelineError(stage="why_card", reason=str(exc)) from exc
