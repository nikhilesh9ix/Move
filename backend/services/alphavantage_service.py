"""
Alpha Vantage market data service - more reliable alternative to Yahoo Finance.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlphaVantageService:
    """Service for fetching market data from Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        """Initialize with Alpha Vantage API key."""
        self.api_key = api_key

    def get_stock_data(self, symbol: str, target_date: str) -> Dict:
        """
        Fetch stock data for a specific date using Alpha Vantage.

        Args:
            symbol: Stock ticker symbol
            target_date: Date in YYYY-MM-DD format

        Returns:
            Dictionary containing stock metrics
        """
        try:
            # Get daily time series data
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "compact",  # Last 100 days
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise ValueError(f"Invalid symbol: {symbol}")

            if "Note" in data:
                raise ValueError(
                    "API rate limit reached. Please wait a minute and try again."
                )

            time_series = data.get("Time Series (Daily)", {})

            if target_date not in time_series:
                raise ValueError(f"No data available for {symbol} on {target_date}")

            day_data = time_series[target_date]

            # Calculate metrics
            open_price = float(day_data["1. open"])
            close_price = float(day_data["4. close"])
            high_price = float(day_data["2. high"])
            low_price = float(day_data["3. low"])
            volume = int(day_data["5. volume"])

            price_change = close_price - open_price
            price_change_percent = (price_change / open_price) * 100

            # Calculate 20-day average volume
            volumes = []
            for date_str in sorted(time_series.keys(), reverse=True)[:20]:
                volumes.append(int(time_series[date_str]["5. volume"]))

            avg_volume_20d = sum(volumes) / len(volumes) if volumes else volume
            volume_ratio = volume / avg_volume_20d if avg_volume_20d > 0 else 1.0

            # Get market performance (S&P 500)
            market_perf = self._get_index_performance(target_date)

            return {
                "symbol": symbol,
                "date": target_date,
                "open": round(open_price, 2),
                "close": round(close_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "volume": volume,
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "avg_volume_20d": int(avg_volume_20d),
                "volume_ratio": round(volume_ratio, 2),
                "market_performance": market_perf,
                "sector_info": None,  # Would need additional API call
                "sector_performance": None,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage API error: {str(e)}")
            raise ValueError(f"Error fetching data from Alpha Vantage: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Alpha Vantage service: {str(e)}")
            raise

    def _get_index_performance(self, target_date: str) -> Optional[Dict]:
        """Get S&P 500 performance for the target date."""
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": "SPY",  # S&P 500 ETF as proxy
                "apikey": self.api_key,
                "outputsize": "compact",
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            time_series = data.get("Time Series (Daily)", {})

            if target_date not in time_series:
                return None

            day_data = time_series[target_date]
            open_price = float(day_data["1. open"])
            close_price = float(day_data["4. close"])
            change_percent = ((close_price - open_price) / open_price) * 100

            return {
                "index": "S&P 500",
                "symbol": "SPY",
                "change_percent": round(change_percent, 2),
            }
        except Exception as e:
            logger.warning(f"Could not fetch index performance: {str(e)}")
            return None
