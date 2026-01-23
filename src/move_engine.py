"""
Move Engine - Main Orchestrator
Coordinates all modules to generate comprehensive stock movement explanations.
"""

from typing import Dict, Optional
from src.market_data import MarketDataFetcher
from src.news_data import NewsDataFetcher
from src.analyzer import ContextualAnalyzer
from src.ai_engine import AIExplanationEngine


class MoveEngine:
    """Main engine that orchestrates the 'Why Did This Move?' analysis."""
    
    def __init__(self):
        """Initialize all sub-modules."""
        self.market_data = MarketDataFetcher()
        self.news_data = NewsDataFetcher()
        self.analyzer = ContextualAnalyzer()
        self.ai_engine = AIExplanationEngine()
    
    def explain_move(
        self,
        symbol: str,
        date: str,
        market_index: str = "^GSPC",
        include_raw_data: bool = False
    ) -> Dict:
        """
        Generate a complete explanation for why a stock moved on a specific day.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")
            date: Date in YYYY-MM-DD format
            market_index: Market index for comparison (default: S&P 500)
            include_raw_data: Whether to include raw data in response
            
        Returns:
            Comprehensive explanation dictionary
        """
        # Step 1: Analyze market movement
        move_analysis = self.market_data.analyze_move(symbol, date)
        
        # Check if the move is significant enough to explain
        if not move_analysis["requires_explanation"]:
            return {
                "symbol": symbol,
                "date": date,
                "explanation": f"{symbol} had no significant movement on {date}",
                "is_significant": False,
                "price_change_pct": move_analysis["price_metrics"]["price_change_pct"]
            }
        
        # Step 2: Get contextual analysis
        context_analysis = self.analyzer.analyze_performance_context(
            symbol, date, market_index
        )
        
        # Step 3: Fetch relevant news
        news_articles = self.news_data.fetch_news_for_symbol(symbol, date)
        news_summary = self.news_data.summarize_news(news_articles)
        
        # Step 4: Generate AI explanation
        explanation = self.ai_engine.generate_explanation(
            symbol=symbol,
            date=date,
            price_metrics=move_analysis["price_metrics"],
            volume_metrics=move_analysis["volume_metrics"],
            context_analysis=context_analysis,
            news_summary=news_summary
        )
        
        # Add context summary
        explanation["context_summary"] = self.analyzer.generate_context_summary(
            context_analysis
        )
        
        # Optionally include raw data
        if include_raw_data:
            explanation["raw_data"] = {
                "move_analysis": move_analysis,
                "context_analysis": context_analysis,
                "news_articles": news_articles
            }
        
        return explanation
    
    def quick_check(self, symbol: str, date: str) -> Dict:
        """
        Quick check if a stock had significant movement worth explaining.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            
        Returns:
            Quick summary dictionary
        """
        try:
            move_analysis = self.market_data.analyze_move(symbol, date)
            
            return {
                "symbol": symbol,
                "date": date,
                "is_significant": move_analysis["requires_explanation"],
                "price_change_pct": move_analysis["price_metrics"]["price_change_pct"],
                "volume_spike": move_analysis["volume_metrics"]["volume_spike"],
                "classification": move_analysis["market_context"]["classification"]
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "date": date,
                "error": str(e),
                "is_significant": False
            }
    
    def batch_analyze(self, symbols: list, date: str) -> Dict:
        """
        Analyze multiple symbols for the same date.
        
        Args:
            symbols: List of stock ticker symbols
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with results for each symbol
        """
        results = {}
        
        for symbol in symbols:
            try:
                results[symbol] = self.explain_move(symbol, date)
            except Exception as e:
                results[symbol] = {
                    "symbol": symbol,
                    "date": date,
                    "error": str(e)
                }
        
        return results
    
    def get_top_movers(self, symbols: list, date: str, top_n: int = 5) -> list:
        """
        Identify and explain the top movers from a list of symbols.
        
        Args:
            symbols: List of stock ticker symbols
            date: Date in YYYY-MM-DD format
            top_n: Number of top movers to return
            
        Returns:
            List of explanations for top movers
        """
        movers = []
        
        for symbol in symbols:
            try:
                check = self.quick_check(symbol, date)
                if check["is_significant"]:
                    movers.append({
                        "symbol": symbol,
                        "change_pct": abs(check["price_change_pct"]),
                        "data": check
                    })
            except:
                continue
        
        # Sort by absolute price change
        movers.sort(key=lambda x: x["change_pct"], reverse=True)
        
        # Get full explanations for top movers
        top_movers = []
        for mover in movers[:top_n]:
            try:
                explanation = self.explain_move(mover["symbol"], date)
                top_movers.append(explanation)
            except:
                continue
        
        return top_movers
