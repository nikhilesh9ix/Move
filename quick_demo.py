"""
Quick demo script to test the Move Engine
"""

from src.move_engine import MoveEngine
from datetime import datetime, timedelta
import json


def main():
    print("=" * 60)
    print("AI 'Why Did This Move?' Engine - Quick Demo")
    print("=" * 60)
    
    engine = MoveEngine()
    
    # Use a date from a few days ago that should have data
    # January 17, 2026 is a Friday (market open)
    symbol = "AAPL"
    date = "2026-01-17"
    
    print(f"\nAnalyzing {symbol} on {date}...\n")
    
    try:
        # Quick check first
        check = engine.quick_check(symbol, date)
        print(f"Quick Check Results:")
        print(f"  Price Change: {check.get('price_change_pct', 'N/A')}%")
        print(f"  Significant: {check.get('is_significant', False)}")
        print(f"  Volume Spike: {check.get('volume_spike', False)}")
        print(f"  Classification: {check.get('classification', 'N/A')}")
        
        if check.get('is_significant'):
            print(f"\n{'='*60}")
            print("Generating full explanation...")
            print(f"{'='*60}\n")
            
            explanation = engine.explain_move(symbol, date)
            
            print(f"Symbol: {explanation['symbol']}")
            print(f"Date: {explanation['date']}")
            print(f"Price Change: {explanation['price_change_pct']}%")
            print(f"Classification: {explanation['move_classification']}")
            print(f"Confidence: {explanation['confidence']:.2f}")
            
            print(f"\nPRIMARY DRIVER:")
            print(f"  {explanation['primary_driver']}")
            
            if explanation['supporting_factors']:
                print(f"\nSUPPORTING FACTORS:")
                for factor in explanation['supporting_factors']:
                    print(f"  • {factor}")
            
            print(f"\nEXPLANATION:")
            print(f"  {explanation['explanation']}")
            
            if explanation.get('news_headlines'):
                print(f"\nTOP NEWS:")
                for headline in explanation['news_headlines'][:3]:
                    print(f"  • {headline['title']}")
                    print(f"    ({headline['source']})")
        else:
            print(f"\n{symbol} had no significant movement on {date}")
    
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTrying with an older date that definitely has data...")
        
        # Try with December 2025
        date = "2025-12-20"
        print(f"\nAnalyzing {symbol} on {date}...\n")
        
        try:
            explanation = engine.explain_move(symbol, date)
            print(f"SUCCESS! Price Change: {explanation.get('price_change_pct', 'N/A')}%")
            print(f"\nFull explanation:\n{json.dumps(explanation, indent=2)}")
        except Exception as e2:
            print(f"Error: {e2}")
            print("\nNote: Market data requires internet connection and may have delays.")


if __name__ == "__main__":
    main()
