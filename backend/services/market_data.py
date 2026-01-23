"""
Market data service using Yahoo Finance HTTP API.
Fetches stock data, calculates metrics, and retrieves market/sector performance.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching and analyzing market data using Yahoo Finance API."""

    # Sector ETF mapping for sector performance
    SECTOR_ETFS = {
        "XLK": "Technology",
        "XLF": "Financials",
        "XLV": "Healthcare",
        "XLE": "Energy",
        "XLY": "Consumer Discretionary",
        "XLP": "Consumer Staples",
        "XLI": "Industrials",
        "XLB": "Materials",
        "XLRE": "Real Estate",
        "XLU": "Utilities",
        "XLC": "Communication Services",
    }

    # Yahoo Finance chart API endpoint (no auth required)
    YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    def __init__(self):
        """Initialize the market data service."""
        self.session = requests.Session()
        # Add user agent to avoid being blocked
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def _datetime_to_unix(self, dt: datetime) -> int:
        """Convert datetime to Unix timestamp."""
        return int(dt.timestamp())

    def _fetch_yahoo_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        max_retries: int = 3,
    ) -> List[Dict]:
        """
        Fetch historical data from Yahoo Finance Chart API.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date for data
            end_date: End date for data
            max_retries: Maximum number of retry attempts

        Returns:
            List of dictionaries containing daily stock data

        Raises:
            ValueError: If data cannot be fetched or parsed
        """
        period1 = self._datetime_to_unix(start_date)
        period2 = self._datetime_to_unix(end_date)

        url = self.YAHOO_CHART_URL.format(symbol=symbol)
        params = {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                # Check for errors in response
                if "chart" not in data or "result" not in data["chart"]:
                    raise ValueError(f"Invalid response format for {symbol}")

                result = data["chart"]["result"]
                if not result or len(result) == 0:
                    raise ValueError(f"No data available for {symbol}")

                result = result[0]

                # Extract timestamps and indicators
                timestamps = result.get("timestamp", [])
                indicators = result.get("indicators", {})
                quote = indicators.get("quote", [{}])[0]

                if not timestamps:
                    raise ValueError(f"No timestamp data for {symbol}")

                # Build list of daily data
                historical_data = []
                for i, ts in enumerate(timestamps):
                    try:
                        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                        historical_data.append(
                            {
                                "Date": date_str,
                                "Open": (
                                    float(quote["open"][i])
                                    if quote.get("open")
                                    and quote["open"][i] is not None
                                    else None
                                ),
                                "High": (
                                    float(quote["high"][i])
                                    if quote.get("high")
                                    and quote["high"][i] is not None
                                    else None
                                ),
                                "Low": (
                                    float(quote["low"][i])
                                    if quote.get("low") and quote["low"][i] is not None
                                    else None
                                ),
                                "Close": (
                                    float(quote["close"][i])
                                    if quote.get("close")
                                    and quote["close"][i] is not None
                                    else None
                                ),
                                "Volume": (
                                    int(quote["volume"][i])
                                    if quote.get("volume")
                                    and quote["volume"][i] is not None
                                    else 0
                                ),
                            }
                        )
                    except (ValueError, KeyError, TypeError, IndexError) as e:
                        logger.warning(
                            f"Skipping invalid data point for {symbol} at index {i}: {e}"
                        )
                        continue

                # Filter out entries with None values
                historical_data = [
                    d
                    for d in historical_data
                    if d["Open"] is not None and d["Close"] is not None
                ]

                if not historical_data:
                    raise ValueError(f"No valid data returned for {symbol}")

                return historical_data

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for {symbol}: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    raise ValueError(
                        f"Failed to fetch data for {symbol} after {max_retries} attempts: {e}"
                    )
            except Exception as e:
                raise ValueError(f"Error parsing data for {symbol}: {e}")

    def get_stock_data(self, symbol: str, target_date: str) -> Dict:
        """
        Fetch comprehensive stock data for a given symbol and date.

        Args:
            symbol: Stock ticker symbol
            target_date: Date in YYYY-MM-DD format

        Returns:
            Dictionary containing stock metrics and context
        """
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")

            # Fetch data for a wider range to calculate metrics
            start_date = target_dt - timedelta(days=30)
            end_date = target_dt + timedelta(days=1)

            # Fetch historical data
            hist_data = self._fetch_yahoo_data(symbol, start_date, end_date)

            # Find target date data
            target_data = None
            for row in hist_data:
                if row["Date"] == target_date:
                    target_data = row
                    break

            if not target_data:
                raise ValueError(f"No data available for {symbol} on {target_date}")

            # Calculate price change
            open_price = target_data["Open"]
            close_price = target_data["Close"]
            price_change = close_price - open_price
            price_change_percent = (price_change / open_price) * 100

            # Calculate 20-day average volume
            volumes = [row["Volume"] for row in hist_data[-20:] if row["Volume"] > 0]
            avg_volume_20d = sum(volumes) / len(volumes) if volumes else 0
            volume_ratio = (
                target_data["Volume"] / avg_volume_20d if avg_volume_20d > 0 else 1.0
            )

            # Get market performance (S&P 500)
            market_perf = self._get_index_performance("^GSPC", target_date)

            # Get sector performance
            sector_info = self._get_sector_info(symbol)
            sector_perf = None
            if sector_info:
                sector_perf = self._get_sector_performance(
                    sector_info["etf"], target_date
                )

            return {
                "symbol": symbol,
                "date": target_date,
                "open": round(open_price, 2),
                "close": round(close_price, 2),
                "high": round(target_data["High"], 2),
                "low": round(target_data["Low"], 2),
                "volume": int(target_data["Volume"]),
                "price_change": round(price_change, 2),
                "price_change_percent": round(price_change_percent, 2),
                "avg_volume_20d": int(avg_volume_20d),
                "volume_ratio": round(volume_ratio, 2),
                "market_performance": market_perf,
                "sector_info": sector_info,
                "sector_performance": sector_perf,
            }

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {str(e)}")
            raise

    def _get_index_performance(
        self, index_symbol: str, target_date: str
    ) -> Optional[Dict]:
        """Get index performance for the target date."""
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            start_date = target_dt - timedelta(days=5)
            end_date = target_dt + timedelta(days=1)

            hist_data = self._fetch_yahoo_data(index_symbol, start_date, end_date)

            # Find target date data
            target_data = None
            for row in hist_data:
                if row["Date"] == target_date:
                    target_data = row
                    break

            if not target_data:
                return None

            change_percent = (
                (target_data["Close"] - target_data["Open"]) / target_data["Open"]
            ) * 100

            return {
                "index": "S&P 500",
                "symbol": index_symbol,
                "change_percent": round(change_percent, 2),
            }
        except Exception as e:
            logger.warning(f"Could not fetch index performance: {str(e)}")
            return None

    def _get_sector_info(self, symbol: str) -> Optional[Dict]:
        """
        Determine sector for a given stock.

        Note: With direct HTTP API, we use a static mapping for common stocks.
        This provides sector info for popular stocks without additional API calls.
        """
        try:
            # Static mapping for common stocks (can be extended)
            STOCK_SECTOR_MAP = {
                "AAPL": ("Technology", "XLK"),
                "MSFT": ("Technology", "XLK"),
                "GOOGL": ("Communication Services", "XLC"),
                "GOOG": ("Communication Services", "XLC"),
                "AMZN": ("Consumer Cyclical", "XLY"),
                "NVDA": ("Technology", "XLK"),
                "META": ("Communication Services", "XLC"),
                "TSLA": ("Consumer Cyclical", "XLY"),
                "BRK.B": ("Financial Services", "XLF"),
                "JPM": ("Financial Services", "XLF"),
                "JNJ": ("Healthcare", "XLV"),
                "V": ("Financial Services", "XLF"),
                "PG": ("Consumer Defensive", "XLP"),
                "XOM": ("Energy", "XLE"),
                "CVX": ("Energy", "XLE"),
                "BAC": ("Financial Services", "XLF"),
                "ABBV": ("Healthcare", "XLV"),
                "KO": ("Consumer Defensive", "XLP"),
                "PEP": ("Consumer Defensive", "XLP"),
                "COST": ("Consumer Defensive", "XLP"),
                "WMT": ("Consumer Defensive", "XLP"),
                "DIS": ("Communication Services", "XLC"),
                "NFLX": ("Communication Services", "XLC"),
                "INTC": ("Technology", "XLK"),
                "AMD": ("Technology", "XLK"),
            }

            if symbol in STOCK_SECTOR_MAP:
                sector, etf = STOCK_SECTOR_MAP[symbol]
                return {"sector": sector, "etf": etf}

            # For unknown stocks, return None (graceful degradation)
            logger.info(f"Sector info not available for {symbol}")
            return None

        except Exception as e:
            logger.warning(f"Could not determine sector for {symbol}: {str(e)}")
            return None

    def _get_sector_performance(
        self, etf_symbol: str, target_date: str
    ) -> Optional[Dict]:
        """Get sector performance using ETF proxy."""
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            start_date = target_dt - timedelta(days=5)
            end_date = target_dt + timedelta(days=1)

            hist_data = self._fetch_yahoo_data(etf_symbol, start_date, end_date)

            # Find target date data
            target_data = None
            for row in hist_data:
                if row["Date"] == target_date:
                    target_data = row
                    break

            if not target_data:
                return None

            change_percent = (
                (target_data["Close"] - target_data["Open"]) / target_data["Open"]
            ) * 100

            return {"etf": etf_symbol, "change_percent": round(change_percent, 2)}
        except Exception as e:
            logger.warning(f"Could not fetch sector performance: {str(e)}")
            return None


# Global instance
market_data_service = MarketDataService()
