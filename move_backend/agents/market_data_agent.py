from __future__ import annotations

from agents.base_agent import BaseAgent
from core.logging import get_logger
from data.market_provider import get_price_data
from models.schemas import MarketDataQuery, PriceData

logger = get_logger(__name__)


class MarketDataAgent(BaseAgent[MarketDataQuery, PriceData]):
    """Fetches a price snapshot for (stock, date).

    Attempts yfinance first (cached 60s); falls back to deterministic mock on
    any network/data failure so the pipeline never hard-stops.
    """

    name = "market_data"

    async def run(self, input_data: MarketDataQuery) -> PriceData:
        logger.info(
            "stage=price_fetch stock=%s date=%s",
            input_data.stock,
            input_data.date,
        )

        result = await get_price_data(input_data.stock)

        logger.info(
            "stage=price_fetch_complete stock=%s price_change=%.2f "
            "direction=%s source=%s",
            result.stock,
            result.price_change,
            result.direction,
            result.source,
        )
        return result
