"""
Service for fetching and processing market data (Yahoo Finance)
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional

INDEX_SYMBOL = "^GSPC"  # S&P 500
SECTOR_ETFS = {
    "TECH": "XLK",
    "FINANCE": "XLF",
    "HEALTH": "XLV",
    "ENERGY": "XLE",
    "CONSUMER": "XLY",
    # Add more as needed
}

class MarketDataService:
    def __init__(self):
        pass

    def fetch_daily_data(self, symbol: str, date: str) -> Optional[Dict]:
        df = yf.download(symbol, start=date, end=date, progress=False)
        if df.empty:
            return None
        row = df.iloc[0]
        return {
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        }

    def fetch_20d_avg_volume(self, symbol: str, date: str) -> Optional[float]:
        df = yf.download(symbol, end=date, period="1mo", progress=False)
        if df.empty or len(df) < 10:
            return None
        return float(df["Volume"].tail(20).mean())

    def fetch_index_performance(self, date: str) -> Optional[float]:
        df = yf.download(INDEX_SYMBOL, start=date, end=date, progress=False)
        if df.empty:
            return None
        row = df.iloc[0]
        return float(row["Close"])

    def fetch_sector_performance(self, sector_etf: str, date: str) -> Optional[float]:
        df = yf.download(sector_etf, start=date, end=date, progress=False)
        if df.empty:
            return None
        row = df.iloc[0]
        return float(row["Close"])
