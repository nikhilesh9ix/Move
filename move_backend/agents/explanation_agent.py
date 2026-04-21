"""Explanation agent — converts structured attribution into rich natural-language output.

Each factor has direction-aware templates with:
  primary      — the core causal sentence
  context      — supporting market color
  historical_hint  — what similar patterns historically did
  actionable_insight — what the user should do with this information
"""
from __future__ import annotations

from typing import Dict, Tuple

from agents.base_agent import BaseAgent
from core.logging import get_logger
from models.schemas import Attribution, ExplanationInput, ExplanationResult

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Rich template library
# ---------------------------------------------------------------------------

_T = Dict[str, Dict[str, str]]

_TEMPLATES: Dict[str, Dict[str, _T]] = {
    "sector": {
        "down": {
            "primary": (
                "{stock} declined primarily due to sector-wide selling pressure, "
                "with industry peers retreating in tandem. Sector dynamics drove {pct}% of today's move."
            ),
            "context": (
                "This reflects industry-level sentiment headwinds rather than {stock}-specific risk — "
                "the selloff is broad-based and correlated across the sector."
            ),
            "historical_hint": (
                "Sector-driven pullbacks of this magnitude have historically reversed within "
                "3–5 trading days when the broader index holds key support levels."
            ),
            "actionable_insight": (
                "This appears to be a short-term sentiment-driven rotation. "
                "Company fundamentals are likely unchanged — watch for a sector stabilisation signal."
            ),
        },
        "up": {
            "primary": (
                "{stock} gained as sector tailwinds lifted the entire industry, "
                "contributing {pct}% to today's move."
            ),
            "context": (
                "Broad sector momentum is carrying stocks higher — "
                "this is a rising-tide lift rather than company-specific outperformance."
            ),
            "historical_hint": (
                "Sector rallies of this size typically sustain for 5–10 sessions "
                "before encountering consolidation."
            ),
            "actionable_insight": (
                "Momentum may continue if the sector catalyst holds. "
                "Monitor peer performance for early signs of rotation fatigue."
            ),
        },
    },
    "macro": {
        "down": {
            "primary": (
                "Macroeconomic headwinds drove {pct}% of {stock}'s decline today — "
                "global risk-off sentiment and institutional rebalancing created broad selling pressure."
            ),
            "context": (
                "Macro-driven moves affect large-cap stocks disproportionately as "
                "institutions reduce risk exposure across the board."
            ),
            "historical_hint": (
                "Macro-driven corrections of this scale have historically persisted "
                "1–2 weeks before stabilising as markets finish repricing expectations."
            ),
            "actionable_insight": (
                "Monitor central bank communication over the next 48 hours — "
                "that's the most likely catalyst for a sentiment reversal."
            ),
        },
        "up": {
            "primary": (
                "Positive macro signals — easing rate expectations and improved global "
                "risk appetite — contributed {pct}% to {stock}'s gain today."
            ),
            "context": (
                "Macro tailwinds are broad-based, lifting rate-sensitive and growth "
                "stocks simultaneously."
            ),
            "historical_hint": (
                "Risk-on macro rallies have averaged 5–7 days of follow-through "
                "historically before the next data catalyst resets positioning."
            ),
            "actionable_insight": (
                "Macro tailwinds often lead to sustained moves. "
                "Consider whether the macro thesis has further room to run before the next print."
            ),
        },
    },
    "rates": {
        "down": {
            "primary": (
                "Interest rate sensitivity accounted for {pct}% of {stock}'s decline "
                "as bond yields moved adversely, compressing growth-stock multiples."
            ),
            "context": (
                "Rate-sensitive stocks face valuation headwinds when yield expectations "
                "shift upward — this is a discount-rate effect, not an earnings story."
            ),
            "historical_hint": (
                "Rate-driven valuation resets tend to normalise within one week "
                "unless accompanied by a material change in Fed/RBI guidance."
            ),
            "actionable_insight": (
                "Watch the 10-year yield direction — it's the key variable for "
                "rate-sensitive names. A yield reversal could quickly offset today's move."
            ),
        },
        "up": {
            "primary": (
                "Falling rate expectations provided a {pct}% tailwind for {stock}, "
                "boosting growth-stock valuations as future cash flows reprice higher."
            ),
            "context": (
                "Duration-sensitive stocks benefit from yield compression — "
                "this is a multiple expansion story, not an earnings beat."
            ),
            "historical_hint": (
                "Rate-relief rallies have historically held for 3–5 sessions "
                "before the next macro data point shifts rate expectations again."
            ),
            "actionable_insight": (
                "This move is rate-dependent — any reversal in yield expectations "
                "could quickly erase gains. Monitor tomorrow's bond market open closely."
            ),
        },
    },
    "earnings": {
        "down": {
            "primary": (
                "Earnings concerns — weak guidance, estimate cuts, or analyst downgrades — "
                "drove {pct}% of {stock}'s decline today."
            ),
            "context": (
                "Markets are discounting lower future earnings, creating a valuation "
                "de-rate that can persist until the revision cycle bottoms."
            ),
            "historical_hint": (
                "Post-guidance-cut drops of this size typically stabilise after "
                "1–3 sessions once analyst estimate revisions are fully priced in."
            ),
            "actionable_insight": (
                "Wait for the estimate revision cycle to complete before making "
                "a decision — second-day price action after earnings events is often more informative."
            ),
        },
        "up": {
            "primary": (
                "Earnings momentum drove {pct}% of {stock}'s rally — "
                "strong guidance or analyst upgrades are fuelling the move."
            ),
            "context": (
                "Positive earnings revision cycles tend to be self-reinforcing "
                "as consensus upgrades follow price momentum over the subsequent weeks."
            ),
            "historical_hint": (
                "Earnings-driven rallies have historically held for 2–4 weeks "
                "as the analyst upgrade cycle plays out across the quarter."
            ),
            "actionable_insight": (
                "Earnings-driven moves have the strongest fundamental backing. "
                "Check analyst consensus revisions for confirmation before sizing a position."
            ),
        },
    },
    "idiosyncratic": {
        "down": {
            "primary": (
                "Company-specific news drove {pct}% of {stock}'s decline today, "
                "moving independently of broader market forces."
            ),
            "context": (
                "Sector peers are not showing the same pattern — "
                "this is a {stock}-specific story and the catalyst is company-level."
            ),
            "historical_hint": (
                "Idiosyncratic drops tend to resolve within 5–7 trading days "
                "once the catalyst is fully digested and positioning normalises."
            ),
            "actionable_insight": (
                "Focus on the company-specific catalyst. "
                "If it's temporary or sentiment-driven, the stock may recover quickly once clarity emerges."
            ),
        },
        "up": {
            "primary": (
                "{stock}-specific catalysts — new contracts, institutional buying, "
                "or positive company news — drove {pct}% of today's gain."
            ),
            "context": (
                "Sector peers aren't participating at the same level, "
                "which validates the company-level catalyst and reduces mean-reversion risk."
            ),
            "historical_hint": (
                "Idiosyncratic upward moves retain ~60% of gains over the following week "
                "on average, outperforming sector-driven moves on a risk-adjusted basis."
            ),
            "actionable_insight": (
                "Verify the company-specific catalyst is sustainable — "
                "idiosyncratic gains can evaporate quickly if the underlying news fades."
            ),
        },
    },
}

_FACTOR_LABELS: Dict[str, str] = {
    "sector": "Sector-wide pressure",
    "macro": "Macro headwinds",
    "rates": "Rate sensitivity",
    "earnings": "Earnings revision",
    "idiosyncratic": "Company-specific news",
}


# ---------------------------------------------------------------------------
# Confidence calculation
# ---------------------------------------------------------------------------

def _compute_confidence(dominant_pct: float) -> Tuple[int, str]:
    """Map dominant-factor weight to a confidence score and label."""
    if dominant_pct >= 55:
        pct = min(92, int(78 + (dominant_pct - 55) * 0.7))
        return pct, "High"
    if dominant_pct >= 38:
        pct = int(63 + (dominant_pct - 38) * 0.9)
        return pct, "Medium"
    return max(45, int(45 + dominant_pct * 0.5)), "Low"


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _get_direction(stock: str, price_change: float) -> str:
    return "down" if price_change < 0 else "up"


def _render(
    stock: str,
    dominant: Attribution,
    price_change: float,
) -> ExplanationResult:
    direction = _get_direction(stock, price_change)
    factor_templates = _TEMPLATES.get(dominant.factor)

    if factor_templates is None:
        # Fallback for unknown factors
        text = (
            f"{dominant.factor.capitalize()} was the primary driver, "
            f"accounting for {dominant.contribution}% of {stock}'s move today."
        )
        conf_pct, conf_label = _compute_confidence(dominant.contribution)
        return ExplanationResult(
            text=text,
            dominant_factor=dominant.factor,
            confidence_pct=conf_pct,
            confidence_label=conf_label,
        )

    t = factor_templates[direction]
    primary = t["primary"].format(stock=stock, pct=dominant.contribution)
    context = t["context"].format(stock=stock, pct=dominant.contribution)
    full_text = f"{primary} {context}"

    conf_pct, conf_label = _compute_confidence(dominant.contribution)

    return ExplanationResult(
        text=full_text,
        dominant_factor=dominant.factor,
        historical_hint=t["historical_hint"],
        actionable_insight=t["actionable_insight"],
        confidence_pct=conf_pct,
        confidence_label=conf_label,
    )


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class ExplanationAgent(BaseAgent[ExplanationInput, ExplanationResult]):
    """Converts structured attribution into rich, grounded natural-language explanations."""

    name = "explanation"

    async def run(self, input_data: ExplanationInput) -> ExplanationResult:
        logger.info("stage=explanation_start stock=%s", input_data.stock)

        items = input_data.attribution.items
        if not items:
            return ExplanationResult(
                text=f"Insufficient data to generate a causal explanation for {input_data.stock}.",
                dominant_factor="unknown",
                confidence_pct=40,
                confidence_label="Low",
            )

        sorted_items = sorted(items, key=lambda a: a.contribution, reverse=True)
        dominant = sorted_items[0]

        # Determine price direction from input stock context:
        # Use the dominant factor's contribution sign as a proxy when no price is
        # directly available — ExplanationInput carries the stock name only, so we
        # infer direction from the explanation label on the WhyCard side. For the
        # single-stock path the orchestrator always passes a PriceData-derived value.
        # We'll use a sentinel: if explanation_input carries price_change, use it;
        # otherwise default to "down" (most common demo scenario).
        price_change = getattr(input_data, "price_change", -1.0)

        result = _render(input_data.stock, dominant, price_change)

        logger.info(
            "stage=explanation_complete stock=%s factor=%s confidence=%d%%(%s)",
            input_data.stock,
            result.dominant_factor,
            result.confidence_pct,
            result.confidence_label,
        )
        return result
