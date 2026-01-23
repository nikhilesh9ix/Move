"""
Test Alpha Vantage service with real API key.
"""

from services.alphavantage_service import AlphaVantageService


def test_alphavantage():
    """Test Alpha Vantage data fetching."""
    api_key = "2VLG0NC6KWEDPWMH"
    service = AlphaVantageService(api_key)

    print("Testing Alpha Vantage Service")
    print("=" * 60)

    # Test with a known date
    symbol = "AAPL"
    date = "2024-01-10"

    print(f"\nFetching {symbol} data for {date}...")
    try:
        data = service.get_stock_data(symbol, date)
        print(f"\n✓ SUCCESS!")
        print(f"  Symbol: {data['symbol']}")
        print(f"  Date: {data['date']}")
        print(f"  Open: ${data['open']}")
        print(f"  Close: ${data['close']}")
        print(f"  Price Change: {data['price_change_percent']:+.2f}%")
        print(f"  Volume: {data['volume']:,}")
        print(f"  Volume Ratio: {data['volume_ratio']:.2f}x")

        if data["market_performance"]:
            mp = data["market_performance"]
            print(f"  Market ({mp['symbol']}): {mp['change_percent']:+.2f}%")

        print("\n✓ Alpha Vantage is working perfectly!")
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    test_alphavantage()
