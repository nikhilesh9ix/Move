"""
Quick test script to verify yfinance is working correctly.
"""

import yfinance as yf
from datetime import datetime, timedelta


def test_yfinance():
    """Test if yfinance can fetch data."""
    print("Testing yfinance data fetching...")
    print("=" * 50)

    # Test 1: Recent data
    symbol = "AAPL"
    print(f"\nTest 1: Fetching recent data for {symbol}")
    ticker = yf.Ticker(symbol)

    # Get last 5 days of data
    hist = ticker.history(period="5d")
    print(f"Retrieved {len(hist)} days of data")
    if not hist.empty:
        print(hist.tail())
        print("\n✓ yfinance is working!")
    else:
        print("\n✗ No data retrieved")

    # Test 2: Specific date
    print(f"\nTest 2: Fetching data for specific date range")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    hist2 = ticker.history(start=start_date, end=end_date)
    print(f"Retrieved {len(hist2)} days of data")
    if not hist2.empty:
        latest_date = hist2.index[-1].strftime("%Y-%m-%d")
        print(f"Latest available date: {latest_date}")
        print(f"Latest close price: ${hist2['Close'].iloc[-1]:.2f}")
        print("\n✓ Date range fetching works!")
    else:
        print("\n✗ No data for date range")

    # Test 3: Stock info
    print(f"\nTest 3: Fetching stock info")
    try:
        info = ticker.info
        sector = info.get("sector", "Unknown")
        print(f"Sector: {sector}")
        print("\n✓ Stock info works!")
    except Exception as e:
        print(f"\n✗ Error fetching info: {e}")


if __name__ == "__main__":
    test_yfinance()
