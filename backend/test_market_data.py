"""
Direct test of market data service with better error handling.
"""

from services.market_data import market_data_service
from datetime import datetime, timedelta


def test_market_data():
    """Test market data fetching with various dates."""
    print("Testing Market Data Service")
    print("=" * 60)

    # Get a recent trading day (not today, not weekend)
    today = datetime.now()
    # Go back to find a weekday
    test_date = today - timedelta(days=7)
    while test_date.weekday() >= 5:  # Skip weekends
        test_date -= timedelta(days=1)

    date_str = test_date.strftime("%Y-%m-%d")

    print(f"\nTest 1: AAPL on {date_str}")
    try:
        data = market_data_service.get_stock_data("AAPL", date_str)
        print(f"✓ Success! Price change: {data['price_change_percent']:.2f}%")
        print(f"  Open: ${data['open']}, Close: ${data['close']}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Try an older date
    old_date = "2024-01-10"
    print(f"\nTest 2: NVDA on {old_date}")
    try:
        data = market_data_service.get_stock_data("NVDA", old_date)
        print(f"✓ Success! Price change: {data['price_change_percent']:.2f}%")
        print(f"  Open: ${data['open']}, Close: ${data['close']}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Try even older
    older_date = "2023-06-15"
    print(f"\nTest 3: MSFT on {older_date}")
    try:
        data = market_data_service.get_stock_data("MSFT", older_date)
        print(f"✓ Success! Price change: {data['price_change_percent']:.2f}%")
        print(f"  Open: ${data['open']}, Close: ${data['close']}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_market_data()
