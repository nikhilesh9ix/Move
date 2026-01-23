"""
Market Data Module
Fetches OHLC data from Yahoo Finance and detects price/volume anomalies.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import numpy as np


class MarketDataFetcher:
    """Fetches and analyzes market data from Yahoo Finance."""
    
    def __init__(self, lookback_days: int = 30):
        """
        Initialize the market data fetcher.
        
        Args:
            lookback_days: Number of days to look back for calculating averages
        """
        self.lookback_days = lookback_days
    
    def fetch_stock_data(self, symbol: str, date: str, extended_lookback: int = 60) -> pd.DataFrame:
        """
        Fetch stock data for a given symbol around a specific date.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")
            date: Date in YYYY-MM-DD format
            extended_lookback: Days to fetch before the target date
            
        Returns:
            DataFrame with OHLC and volume data
        """
        target_date = pd.to_datetime(date)
        start_date = target_date - timedelta(days=extended_lookback)
        end_date = target_date + timedelta(days=1)
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol} on {date}")
        
        return df
    
    def get_day_data(self, symbol: str, date: str) -> Dict:
        """
        Get detailed data for a specific trading day.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with day's trading data
        """
        df = self.fetch_stock_data(symbol, date)
        target_date = pd.to_datetime(date)
        
        # Get the target day's data
        target_day = df[df.index.date == target_date.date()]
        
        if target_day.empty:
            raise ValueError(f"No trading data for {symbol} on {date}")
        
        day_data = target_day.iloc[0]
        
        return {
            "symbol": symbol,
            "date": date,
            "open": float(day_data["Open"]),
            "high": float(day_data["High"]),
            "low": float(day_data["Low"]),
            "close": float(day_data["Close"]),
            "volume": int(day_data["Volume"]),
            "previous_close": float(df.iloc[-2]["Close"]) if len(df) > 1 else None
        }
    
    def calculate_price_change(self, symbol: str, date: str) -> Dict:
        """
        Calculate price change metrics for a given day.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with price change metrics
        """
        day_data = self.get_day_data(symbol, date)
        
        if day_data["previous_close"] is None:
            return {
                "price_change_pct": 0.0,
                "intraday_change_pct": 0.0,
                "is_significant": False
            }
        
        price_change_pct = ((day_data["close"] - day_data["previous_close"]) 
                           / day_data["previous_close"] * 100)
        
        intraday_change_pct = ((day_data["close"] - day_data["open"]) 
                              / day_data["open"] * 100)
        
        return {
            "price_change_pct": round(price_change_pct, 2),
            "intraday_change_pct": round(intraday_change_pct, 2),
            "price_change_abs": round(day_data["close"] - day_data["previous_close"], 2),
            "is_significant": abs(price_change_pct) >= 2.0  # 2% threshold
        }
    
    def detect_volume_anomaly(self, symbol: str, date: str) -> Dict:
        """
        Detect volume anomalies by comparing to historical average.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with volume anomaly metrics
        """
        df = self.fetch_stock_data(symbol, date, extended_lookback=self.lookback_days + 10)
        target_date = pd.to_datetime(date)
        
        # Get historical data before target date
        historical = df[df.index < target_date].tail(self.lookback_days)
        target_day = df[df.index.date == target_date.date()]
        
        if historical.empty or target_day.empty:
            return {
                "volume_spike": False,
                "volume_ratio": 1.0,
                "avg_volume": 0
            }
        
        avg_volume = historical["Volume"].mean()
        target_volume = int(target_day.iloc[0]["Volume"])
        volume_ratio = target_volume / avg_volume if avg_volume > 0 else 1.0
        
        return {
            "volume": target_volume,
            "avg_volume": int(avg_volume),
            "volume_ratio": round(volume_ratio, 2),
            "volume_spike": volume_ratio >= 1.5  # 50% above average
        }
    
    def get_market_context(self, symbol: str, date: str, market_index: str = "^GSPC") -> Dict:
        """
        Get market-wide context by comparing to a market index.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            market_index: Market index symbol (default: S&P 500)
            
        Returns:
            Dictionary with market context
        """
        stock_change = self.calculate_price_change(symbol, date)
        market_change = self.calculate_price_change(market_index, date)
        
        # Determine if the move is correlated with the market
        stock_pct = stock_change["price_change_pct"]
        market_pct = market_change["price_change_pct"]
        
        # Check if both moved in the same direction
        same_direction = (stock_pct * market_pct) > 0
        
        # Calculate relative strength
        relative_strength = stock_pct - market_pct
        
        # Classify the move
        if abs(relative_strength) < 1.0:
            classification = "market_driven"
        elif same_direction and abs(relative_strength) < 3.0:
            classification = "market_influenced"
        else:
            classification = "stock_specific"
        
        return {
            "stock_change_pct": stock_pct,
            "market_change_pct": market_pct,
            "relative_strength": round(relative_strength, 2),
            "classification": classification,
            "market_index": market_index
        }
    
    def analyze_move(self, symbol: str, date: str) -> Dict:
        """
        Comprehensive analysis of a stock's movement on a given day.
        
        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format
            
        Returns:
            Complete analysis dictionary
        """
        day_data = self.get_day_data(symbol, date)
        price_metrics = self.calculate_price_change(symbol, date)
        volume_metrics = self.detect_volume_anomaly(symbol, date)
        market_context = self.get_market_context(symbol, date)
        
        return {
            "symbol": symbol,
            "date": date,
            "price_data": day_data,
            "price_metrics": price_metrics,
            "volume_metrics": volume_metrics,
            "market_context": market_context,
            "requires_explanation": (
                price_metrics["is_significant"] or 
                volume_metrics["volume_spike"]
            )
        }


# Sector mapping for common stocks
SECTOR_INDICES = {
    "technology": "^IXIC",  # NASDAQ
    "finance": "^XLF",
    "healthcare": "^XLV",
    "energy": "^XLE",
    "consumer": "^XLY",
    "default": "^GSPC"  # S&P 500
}


def get_sector_index(symbol: str) -> str:
    """
    Get the appropriate sector index for a stock.
    This is a simplified version - in production, use proper sector data.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Sector index symbol
    """
    # This would ideally use yfinance ticker.info['sector']
    # For now, return the default S&P 500
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        sector = info.get("sector", "").lower()
        
        if "technology" in sector or "communication" in sector:
            return SECTOR_INDICES["technology"]
        elif "financial" in sector:
            return SECTOR_INDICES["finance"]
        elif "health" in sector:
            return SECTOR_INDICES["healthcare"]
        elif "energy" in sector:
            return SECTOR_INDICES["energy"]
        elif "consumer" in sector:
            return SECTOR_INDICES["consumer"]
    except:
        pass
    
    return SECTOR_INDICES["default"]
