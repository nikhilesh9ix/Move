"""
Contextual Analyzer Module
Performs detailed contextual analysis comparing stock performance to market and sector.
"""

from typing import Dict, Optional
from src.market_data import MarketDataFetcher, get_sector_index


class ContextualAnalyzer:
    """Analyzes stock movements in context of market and sector performance."""
    
    def __init__(self):
        """Initialize the contextual analyzer."""
        self.market_data = MarketDataFetcher()
    
    def analyze_performance_context(
        self, 
        symbol: str, 
        date: str,
        market_index: str = "^GSPC",
        sector_index: Optional[str] = None
    ) -> Dict:
        """
        Analyze how a stock's performance compares to market and sector.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            market_index: Market index to compare against (default: S&P 500)
            sector_index: Sector index to compare against (auto-detected if None)
            
        Returns:
            Dictionary with contextual analysis
        """
        # Get stock performance
        stock_change = self.market_data.calculate_price_change(symbol, date)
        stock_volume = self.market_data.detect_volume_anomaly(symbol, date)
        
        # Get market performance
        market_change = self.market_data.calculate_price_change(market_index, date)
        
        # Get sector performance
        if sector_index is None:
            sector_index = get_sector_index(symbol)
        
        sector_change = None
        try:
            sector_change = self.market_data.calculate_price_change(sector_index, date)
        except Exception as e:
            print(f"Could not fetch sector data: {e}")
        
        # Classify the move
        classification = self._classify_move(
            stock_change["price_change_pct"],
            market_change["price_change_pct"],
            sector_change["price_change_pct"] if sector_change else None
        )
        
        # Calculate correlations
        correlations = self._calculate_correlations(
            stock_change["price_change_pct"],
            market_change["price_change_pct"],
            sector_change["price_change_pct"] if sector_change else None
        )
        
        return {
            "stock": {
                "symbol": symbol,
                "change_pct": stock_change["price_change_pct"],
                "volume_spike": stock_volume["volume_spike"],
                "volume_ratio": stock_volume["volume_ratio"]
            },
            "market": {
                "index": market_index,
                "change_pct": market_change["price_change_pct"]
            },
            "sector": {
                "index": sector_index,
                "change_pct": sector_change["price_change_pct"] if sector_change else None
            } if sector_change else None,
            "classification": classification,
            "correlations": correlations,
            "relative_strength": {
                "vs_market": round(stock_change["price_change_pct"] - market_change["price_change_pct"], 2),
                "vs_sector": round(stock_change["price_change_pct"] - sector_change["price_change_pct"], 2) if sector_change else None
            }
        }
    
    def _classify_move(
        self,
        stock_pct: float,
        market_pct: float,
        sector_pct: Optional[float]
    ) -> str:
        """
        Classify whether a move is market-driven, sector-driven, or stock-specific.
        
        Args:
            stock_pct: Stock price change percentage
            market_pct: Market price change percentage
            sector_pct: Sector price change percentage (optional)
            
        Returns:
            Classification string
        """
        # Check if stock and market moved in same direction
        same_direction = (stock_pct * market_pct) > 0
        
        # Calculate relative differences
        market_diff = abs(stock_pct - market_pct)
        
        # Market-driven: stock closely follows market
        if same_direction and market_diff < 1.5:
            return "market_driven"
        
        # Check sector if available
        if sector_pct is not None:
            sector_diff = abs(stock_pct - sector_pct)
            same_direction_sector = (stock_pct * sector_pct) > 0
            
            # Sector-driven: follows sector more than market
            if same_direction_sector and sector_diff < market_diff and sector_diff < 2.0:
                return "sector_driven"
        
        # Stock-specific: significant divergence from market/sector
        if market_diff > 3.0:
            return "stock_specific"
        
        # Mixed influence
        return "mixed_influence"
    
    def _calculate_correlations(
        self,
        stock_pct: float,
        market_pct: float,
        sector_pct: Optional[float]
    ) -> Dict:
        """
        Calculate correlation indicators between stock, market, and sector.
        
        Args:
            stock_pct: Stock price change percentage
            market_pct: Market price change percentage
            sector_pct: Sector price change percentage (optional)
            
        Returns:
            Dictionary with correlation indicators
        """
        correlations = {
            "market_correlation": self._correlation_indicator(stock_pct, market_pct),
            "sector_correlation": None
        }
        
        if sector_pct is not None:
            correlations["sector_correlation"] = self._correlation_indicator(stock_pct, sector_pct)
        
        return correlations
    
    def _correlation_indicator(self, val1: float, val2: float) -> str:
        """
        Simple correlation indicator based on direction and magnitude.
        
        Args:
            val1: First value
            val2: Second value
            
        Returns:
            Correlation strength: "strong", "moderate", "weak", "negative"
        """
        # Check if same direction
        if (val1 * val2) < 0:
            return "negative"
        
        # Calculate difference in magnitude
        diff = abs(val1 - val2)
        
        if diff < 1.0:
            return "strong"
        elif diff < 2.5:
            return "moderate"
        else:
            return "weak"
    
    def generate_context_summary(self, analysis: Dict) -> str:
        """
        Generate a human-readable summary of the contextual analysis.
        
        Args:
            analysis: Analysis dictionary from analyze_performance_context
            
        Returns:
            Summary string
        """
        stock = analysis["stock"]
        market = analysis["market"]
        sector = analysis.get("sector")
        classification = analysis["classification"]
        
        summary_parts = []
        
        # Stock performance
        direction = "rose" if stock["change_pct"] > 0 else "fell"
        summary_parts.append(
            f"{stock['symbol']} {direction} {abs(stock['change_pct'])}%"
        )
        
        # Market context
        market_direction = "up" if market["change_pct"] > 0 else "down"
        summary_parts.append(
            f"while the market was {market_direction} {abs(market['change_pct'])}%"
        )
        
        # Sector context
        if sector and sector["change_pct"] is not None:
            sector_direction = "up" if sector["change_pct"] > 0 else "down"
            summary_parts.append(
                f"and its sector was {sector_direction} {abs(sector['change_pct'])}%"
            )
        
        # Volume
        if stock["volume_spike"]:
            summary_parts.append(
                f"with {stock['volume_ratio']}x normal volume"
            )
        
        # Classification
        classification_text = {
            "market_driven": "This appears to be a market-driven move",
            "sector_driven": "This appears to be a sector-driven move",
            "stock_specific": "This appears to be a stock-specific move",
            "mixed_influence": "This appears to be influenced by multiple factors"
        }.get(classification, "")
        
        if classification_text:
            summary_parts.append(classification_text)
        
        return ". ".join(summary_parts) + "."
    
    def determine_primary_driver(self, analysis: Dict, news_summary: Dict) -> str:
        """
        Determine the most likely primary driver of the move.
        
        Args:
            analysis: Contextual analysis dictionary
            news_summary: News summary dictionary
            
        Returns:
            Primary driver description
        """
        classification = analysis["classification"]
        has_news = news_summary.get("has_significant_news", False)
        volume_spike = analysis["stock"]["volume_spike"]
        
        # Strong news + volume spike + stock-specific = likely news-driven
        if has_news and volume_spike and classification == "stock_specific":
            return "company_specific_news"
        
        # Market-driven with no significant news
        if classification == "market_driven" and not has_news:
            return "market_sentiment"
        
        # Sector-driven
        if classification == "sector_driven":
            return "sector_trend"
        
        # Volume spike without clear news = possible insider/institutional activity
        if volume_spike and not has_news:
            return "unusual_trading_activity"
        
        # Default
        return "multiple_factors"
