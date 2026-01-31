"""
Market data service using Yahoo Finance HTTP API.
Fetches stock data, calculates metrics, and retrieves market/sector performance.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
import time
import statistics

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

    def get_historical_data(
        self, symbol: str, target_date: str, days_back: int = 30
    ) -> List[Dict]:
        """
        Get historical price data with technical indicators.
        
        Args:
            symbol: Stock ticker symbol
            target_date: Target date in YYYY-MM-DD format
            days_back: Number of days of history to fetch
            
        Returns:
            List of historical data points with technical indicators
        """
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            # Fetch extra data for MA calculation
            start_date = target_dt - timedelta(days=days_back + 50)
            end_date = target_dt + timedelta(days=1)
            
            hist_data = self._fetch_yahoo_data(symbol, start_date, end_date)
            
            # Calculate moving averages
            closes = [row["Close"] for row in hist_data if row["Close"] is not None]
            
            result = []
            for i, row in enumerate(hist_data):
                data_point = {
                    "date": row["Date"],
                    "open": round(row["Open"], 2) if row["Open"] else None,
                    "high": round(row["High"], 2) if row["High"] else None,
                    "low": round(row["Low"], 2) if row["Low"] else None,
                    "close": round(row["Close"], 2) if row["Close"] else None,
                    "volume": row["Volume"],
                    "ma_20": None,
                    "ma_50": None,
                }
                
                # Calculate 20-day MA
                if i >= 19:
                    ma_20_data = closes[max(0, i-19):i+1]
                    if len(ma_20_data) >= 20:
                        data_point["ma_20"] = round(sum(ma_20_data) / len(ma_20_data), 2)
                
                # Calculate 50-day MA
                if i >= 49:
                    ma_50_data = closes[max(0, i-49):i+1]
                    if len(ma_50_data) >= 50:
                        data_point["ma_50"] = round(sum(ma_50_data) / len(ma_50_data), 2)
                
                result.append(data_point)
            
            # Return only the requested days
            cutoff_date = target_dt - timedelta(days=days_back)
            result = [
                r for r in result 
                if datetime.strptime(r["date"], "%Y-%m-%d") >= cutoff_date
                and datetime.strptime(r["date"], "%Y-%m-%d") <= target_dt
            ]
            
            logger.info(f"Fetched {len(result)} days of historical data for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return []

    def get_sector_context(
        self, symbol: str, target_date: str
    ) -> Optional[Dict]:
        """
        Get comprehensive sector and market context analysis.
        
        Args:
            symbol: Stock ticker symbol
            target_date: Target date in YYYY-MM-DD format
            
        Returns:
            Dictionary with sector context including market indices and correlations
        """
        try:
            sector_info = self._get_sector_info(symbol)
            if not sector_info:
                return None
            
            # Get stock data for the day
            stock_data = self.get_stock_data(symbol, target_date)
            stock_change = stock_data["price_change_percent"]
            
            # Get sector performance
            sector_perf = self._get_sector_performance(sector_info["etf"], target_date)
            sector_change = sector_perf["change_percent"] if sector_perf else 0
            
            # Get market indices
            sp500_perf = self._get_index_performance("^GSPC", target_date)
            nasdaq_perf = self._get_index_performance("^IXIC", target_date)
            
            sp500_change = sp500_perf["change_percent"] if sp500_perf else 0
            nasdaq_change = nasdaq_perf["change_percent"] if nasdaq_perf else 0
            
            # Calculate relative strength (stock vs sector)
            relative_strength = stock_change - sector_change
            
            # Get peer stocks
            peer_stocks = self._get_peer_stocks(symbol, sector_info["sector"], target_date)
            
            # Calculate correlation (simplified - using same day movement)
            correlation = None
            if sector_change != 0:
                # Simplified correlation indicator
                if (stock_change > 0 and sector_change > 0) or (stock_change < 0 and sector_change < 0):
                    correlation = min(abs(stock_change / sector_change), 1.0) * 0.8
                else:
                    correlation = -0.3
            
            return {
                "sector_name": sector_info["sector"],
                "sector_change_percent": round(sector_change, 2),
                "sp500_change_percent": round(sp500_change, 2),
                "nasdaq_change_percent": round(nasdaq_change, 2),
                "relative_strength": round(relative_strength, 2),
                "correlation_with_sector": round(correlation, 2) if correlation else None,
                "peer_stocks": peer_stocks,
            }
            
        except Exception as e:
            logger.error(f"Error getting sector context: {str(e)}")
            return None

    def _get_peer_stocks(
        self, symbol: str, sector: str, target_date: str
    ) -> List[Dict]:
        """Get performance of peer stocks in the same sector."""
        try:
            # Mapping of sectors to peer stocks
            SECTOR_PEERS = {
                "Technology": ["AAPL", "MSFT", "NVDA", "AMD", "INTC"],
                "Communication Services": ["GOOGL", "META", "DIS", "NFLX"],
                "Consumer Cyclical": ["AMZN", "TSLA"],
                "Financial Services": ["JPM", "BAC", "V", "BRK.B"],
                "Healthcare": ["JNJ", "ABBV"],
                "Consumer Defensive": ["PG", "KO", "PEP", "COST", "WMT"],
                "Energy": ["XOM", "CVX"],
            }
            
            peer_symbols = SECTOR_PEERS.get(sector, [])
            # Remove the current symbol
            peer_symbols = [s for s in peer_symbols if s != symbol][:3]
            
            peer_data = []
            for peer in peer_symbols:
                try:
                    data = self.get_stock_data(peer, target_date)
                    peer_data.append({
                        "symbol": peer,
                        "change_percent": data["price_change_percent"],
                    })
                except Exception as e:
                    logger.warning(f"Could not fetch peer data for {peer}: {str(e)}")
                    continue
            
            return peer_data
            
        except Exception as e:
            logger.warning(f"Error fetching peer stocks: {str(e)}")
            return []

    def get_technical_indicators(
        self, symbol: str, target_date: str
    ) -> Dict:
        """
        Calculate technical indicators for the stock.
        
        Args:
            symbol: Stock ticker symbol
            target_date: Target date in YYYY-MM-DD format
            
        Returns:
            Dictionary with technical indicators
        """
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            start_date = target_dt - timedelta(days=70)
            end_date = target_dt + timedelta(days=1)
            
            hist_data = self._fetch_yahoo_data(symbol, start_date, end_date)
            
            # Find target date index
            target_idx = None
            for i, row in enumerate(hist_data):
                if row["Date"] == target_date:
                    target_idx = i
                    break
            
            if target_idx is None:
                return {}
            
            # Calculate indicators
            closes = [row["Close"] for row in hist_data[:target_idx+1] if row["Close"]]
            volumes = [row["Volume"] for row in hist_data[:target_idx+1] if row["Volume"]]
            
            indicators = {}
            
            # Moving averages
            if len(closes) >= 20:
                indicators["ma_20"] = round(sum(closes[-20:]) / 20, 2)
            if len(closes) >= 50:
                indicators["ma_50"] = round(sum(closes[-50:]) / 50, 2)
            
            # RSI (simplified 14-day)
            if len(closes) >= 15:
                rsi = self._calculate_rsi(closes[-15:])
                indicators["rsi"] = round(rsi, 2) if rsi else None
            
            # Volume analysis
            if len(volumes) >= 20:
                avg_volume = sum(volumes[-20:]) / 20
                indicators["volume_avg_20d"] = int(avg_volume)
                current_volume = volumes[-1]
                indicators["volume_ratio"] = round(current_volume / avg_volume, 2) if avg_volume > 0 else 1.0
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index (RSI)."""
        try:
            if len(prices) < period + 1:
                return None
            
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.warning(f"Error calculating RSI: {str(e)}")
            return None

    def analyze_multi_day_pattern(
        self, symbol: str, end_date: str, days: int = 7
    ) -> Optional[Dict]:
        """
        Analyze multi-day movement patterns.
        
        Args:
            symbol: Stock ticker symbol
            end_date: End date in YYYY-MM-DD format
            days: Number of days to analyze
            
        Returns:
            Dictionary with pattern analysis
        """
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            start_dt = end_dt - timedelta(days=days-1)
            fetch_start = start_dt - timedelta(days=5)
            
            hist_data = self._fetch_yahoo_data(symbol, fetch_start, end_dt + timedelta(days=1))
            
            # Filter to date range
            period_data = [
                row for row in hist_data
                if start_dt <= datetime.strptime(row["Date"], "%Y-%m-%d") <= end_dt
            ]
            
            if not period_data:
                return None
            
            # Calculate cumulative change
            first_open = period_data[0]["Open"]
            last_close = period_data[-1]["Close"]
            cumulative_change = ((last_close - first_open) / first_open) * 100
            
            # Identify pattern type
            daily_changes = [
                ((row["Close"] - row["Open"]) / row["Open"]) * 100
                for row in period_data
            ]
            
            positive_days = sum(1 for change in daily_changes if change > 0)
            negative_days = sum(1 for change in daily_changes if change < 0)
            
            if positive_days >= days * 0.7:
                pattern_type = "Strong Uptrend"
            elif negative_days >= days * 0.7:
                pattern_type = "Strong Downtrend"
            elif abs(cumulative_change) < 2:
                pattern_type = "Consolidation"
            else:
                pattern_type = "Mixed/Volatile"
            
            description = f"Over {days} days: {positive_days} up days, {negative_days} down days. "
            description += f"Cumulative change: {cumulative_change:+.2f}%"
            
            return {
                "pattern_type": pattern_type,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": end_date,
                "cumulative_change": round(cumulative_change, 2),
                "description": description,
                "similar_historical_events": None,  # Can be enhanced with ML
            }
            
        except Exception as e:
            logger.error(f"Error analyzing multi-day pattern: {str(e)}")
            return None


# Global instance
market_data_service = MarketDataService()
