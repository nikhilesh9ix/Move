"""
Evidence builder module.
Compiles all data sources into structured evidence for AI analysis.
"""

from typing import Dict, List
import json


class EvidenceBuilder:
    """Builds structured evidence from market data and news."""

    @staticmethod
    def build_evidence(market_data: Dict, news_items: List[Dict]) -> str:
        """
        Compile all data into a structured text format for AI analysis.

        Args:
            market_data: Market data dictionary from MarketDataService
            news_items: List of news articles from NewsService

        Returns:
            Formatted evidence string
        """
        evidence_parts = []

        # Stock performance section
        evidence_parts.append("=== STOCK PERFORMANCE ===")
        evidence_parts.append(f"Symbol: {market_data['symbol']}")
        evidence_parts.append(f"Date: {market_data['date']}")
        evidence_parts.append(f"Open: ${market_data['open']}")
        evidence_parts.append(f"Close: ${market_data['close']}")
        evidence_parts.append(f"High: ${market_data['high']}")
        evidence_parts.append(f"Low: ${market_data['low']}")
        evidence_parts.append(
            f"Price Change: ${market_data['price_change']} ({market_data['price_change_percent']:+.2f}%)"
        )
        evidence_parts.append("")

        # Volume analysis section
        evidence_parts.append("=== VOLUME ANALYSIS ===")
        evidence_parts.append(f"Volume: {market_data['volume']:,}")
        evidence_parts.append(
            f"20-Day Average Volume: {market_data['avg_volume_20d']:,}"
        )
        evidence_parts.append(
            f"Volume Ratio: {market_data['volume_ratio']:.2f}x average"
        )

        volume_context = "normal"
        if market_data["volume_ratio"] > 2.0:
            volume_context = "significantly elevated (2x+ average)"
        elif market_data["volume_ratio"] > 1.5:
            volume_context = "elevated (1.5x+ average)"
        elif market_data["volume_ratio"] < 0.5:
            volume_context = "below average"

        evidence_parts.append(f"Volume Context: {volume_context}")
        evidence_parts.append("")

        # Market context section
        evidence_parts.append("=== MARKET CONTEXT ===")
        if market_data.get("market_performance"):
            mp = market_data["market_performance"]
            evidence_parts.append(f"{mp['index']}: {mp['change_percent']:+.2f}%")
        else:
            evidence_parts.append("Market data: Not available")

        if market_data.get("sector_info") and market_data.get("sector_performance"):
            si = market_data["sector_info"]
            sp = market_data["sector_performance"]
            evidence_parts.append(f"Sector: {si['sector']}")
            evidence_parts.append(
                f"Sector Performance ({sp['etf']}): {sp['change_percent']:+.2f}%"
            )
        else:
            evidence_parts.append("Sector data: Not available")

        evidence_parts.append("")

        # News section
        evidence_parts.append("=== NEWS HEADLINES ===")
        if news_items:
            for i, article in enumerate(news_items, 1):
                evidence_parts.append(f"{i}. {article['title']}")
                evidence_parts.append(f"   Source: {article['source']}")
                if article.get("description"):
                    evidence_parts.append(f"   {article['description'][:150]}...")
                evidence_parts.append("")
        else:
            evidence_parts.append("No significant news found for this date.")
            evidence_parts.append("")

        return "\n".join(evidence_parts)

    @staticmethod
    def build_json_evidence(market_data: Dict, news_items: List[Dict]) -> Dict:
        """
        Build evidence as a JSON structure (alternative format).

        Args:
            market_data: Market data dictionary
            news_items: List of news articles

        Returns:
            Structured evidence dictionary
        """
        return {
            "stock_performance": {
                "symbol": market_data["symbol"],
                "date": market_data["date"],
                "price_data": {
                    "open": market_data["open"],
                    "close": market_data["close"],
                    "high": market_data["high"],
                    "low": market_data["low"],
                    "change": market_data["price_change"],
                    "change_percent": market_data["price_change_percent"],
                },
            },
            "volume_analysis": {
                "volume": market_data["volume"],
                "avg_volume_20d": market_data["avg_volume_20d"],
                "volume_ratio": market_data["volume_ratio"],
            },
            "market_context": {
                "market_performance": market_data.get("market_performance"),
                "sector_info": market_data.get("sector_info"),
                "sector_performance": market_data.get("sector_performance"),
            },
            "news": news_items,
        }


# Global instance
evidence_builder = EvidenceBuilder()
