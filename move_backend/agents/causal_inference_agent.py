from __future__ import annotations

import hashlib
import random
from typing import List, Optional

from agents.base_agent import BaseAgent
from core.logging import get_logger
from models.schemas import (
    Attribution,
    AttributionResult,
    CausalInferenceInput,
    NewsSignal,
)

logger = get_logger(__name__)

_ALL_FACTORS = ["sector", "macro", "rates", "earnings", "idiosyncratic"]
_FACTORS_PER_ATTRIBUTION = 3
_WEIGHT_LOW = 10.0
_WEIGHT_HIGH = 60.0


def _rng_for(stock: str, price_change: float) -> random.Random:
    key = f"{stock}{price_change}"
    seed_int = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed_int)


def _apply_signal_bias(
    factors: List[str],
    raw_weights: List[float],
    price_change: float,
    news: Optional[NewsSignal],
) -> List[float]:
    """Nudge factor weights based on real signals.

    Rules:
    - Negative news (sentiment < −0.2): boost 'idiosyncratic' (company-specific)
    - Large absolute move (|Δ| > 3%): boost 'sector' and 'macro'
    - Positive news + up move: boost 'earnings'
    All boosts are additive and re-normalised; original RNG structure preserved.
    """
    weights = list(raw_weights)

    def _boost(factor: str, amount: float) -> None:
        if factor in factors:
            idx = factors.index(factor)
            weights[idx] += amount

    abs_change = abs(price_change)
    sentiment = news.sentiment if news else 0.0

    if news and sentiment < -0.2:
        _boost("idiosyncratic", 20.0)

    if abs_change > 3.0:
        _boost("sector", 15.0)
        _boost("macro", 10.0)

    if news and sentiment > 0.2 and price_change > 0:
        _boost("earnings", 18.0)

    return weights


class CausalInferenceAgent(BaseAgent[CausalInferenceInput, AttributionResult]):
    """Decomposes a price move into factor contributions that sum to exactly 100.

    Base weights are deterministic (seeded by stock+price_change). When a
    NewsSignal is provided, weights are nudged toward plausible real-world
    causes before normalisation. Sum invariant is always preserved.
    """

    name = "causal_inference"

    async def run(self, input_data: CausalInferenceInput) -> AttributionResult:
        price_data = input_data.price_data
        news = input_data.news_signal

        logger.info(
            "stage=attribution_start stock=%s price_change=%.2f has_news=%s",
            price_data.stock,
            price_data.price_change,
            news is not None,
        )

        rng = _rng_for(price_data.stock, price_data.price_change)
        factors = rng.sample(_ALL_FACTORS, _FACTORS_PER_ATTRIBUTION)
        raw_weights = [rng.uniform(_WEIGHT_LOW, _WEIGHT_HIGH) for _ in factors]

        # Apply signal-driven bias if real data is available
        biased_weights = _apply_signal_bias(
            factors, raw_weights, price_data.price_change, news
        )
        total = sum(biased_weights)

        # Normalise to 100; last bucket absorbs rounding drift
        contributions: List[float] = []
        running = 0.0
        for i, w in enumerate(biased_weights):
            if i < len(biased_weights) - 1:
                pct = round(w / total * 100, 1)
                contributions.append(pct)
                running += pct
            else:
                contributions.append(round(100.0 - running, 1))

        items = [
            Attribution(factor=f, contribution=c)
            for f, c in zip(factors, contributions)
        ]
        result = AttributionResult(items=items)

        logger.info(
            "stage=attribution_complete stock=%s dominant_factor=%s "
            "dominant_pct=%.1f news_sentiment=%s",
            price_data.stock,
            result.dominant().factor,
            result.dominant().contribution,
            f"{news.sentiment:.2f}" if news else "n/a",
        )
        return result
