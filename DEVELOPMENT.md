# AI "Why Did This Move?" Engine - Development Guide

## Setup Instructions

### 1. Environment Setup

```bash
# Navigate to project directory
cd Move

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required:
#   - OPENROUTER_API_KEY (for AI explanations)
#   - NEWSAPI_KEY (for news data)
```

### 3. Get API Keys

**OpenRouter API Key:**
1. Go to https://openrouter.ai/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new key
5. Add to `.env` as `OPENROUTER_API_KEY`

**NewsAPI Key:**
1. Go to https://newsapi.org/
2. Sign up for free account
3. Get your API key
4. Add to `.env` as `NEWSAPI_KEY`

## Running the Application

### Command Line Usage

```python
# Run example scripts
python examples/example_usage.py

# Or use directly in Python
from src.move_engine import MoveEngine

engine = MoveEngine()
explanation = engine.explain_move("AAPL", "2024-01-15")
print(explanation)
```

### API Server

```bash
# Start the API server
python -m uvicorn api.main:app --reload

# Or specify host/port
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Examples

```bash
# Health check
curl http://localhost:8000/health

# Explain a stock movement
curl -X POST "http://localhost:8000/explain" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "date": "2024-01-15"}'

# Quick check
curl -X POST "http://localhost:8000/quick-check" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "date": "2024-01-15"}'

# Get popular symbols
curl http://localhost:8000/symbols/popular
```

## Testing

```bash
# Run unit tests
pytest tests/test_move_engine.py -v

# Test API endpoints (requires server running)
python tests/test_api.py
```

## Project Structure

```
Move/
├── src/
│   ├── market_data.py      # Yahoo Finance data fetching
│   ├── news_data.py         # News article retrieval
│   ├── analyzer.py          # Contextual analysis
│   ├── ai_engine.py         # LLM-based explanation
│   └── move_engine.py       # Main orchestrator
├── api/
│   └── main.py              # FastAPI application
├── tests/
│   ├── test_move_engine.py  # Unit tests
│   └── test_api.py          # API tests
├── examples/
│   └── example_usage.py     # Usage examples
└── requirements.txt         # Dependencies
```

## Key Components

### 1. Market Data Module (`src/market_data.py`)
- Fetches OHLC data from Yahoo Finance
- Detects price and volume anomalies
- Calculates market context

### 2. News Data Module (`src/news_data.py`)
- Fetches news from NewsAPI and Google News RSS
- Filters and deduplicates articles
- Identifies significant news events

### 3. Contextual Analyzer (`src/analyzer.py`)
- Compares stock vs market vs sector performance
- Classifies moves (market-driven, sector-driven, stock-specific)
- Generates context summaries

### 4. AI Engine (`src/ai_engine.py`)
- Uses OpenRouter LLMs for explanation generation
- Performs evidence-based reasoning
- Calculates confidence scores

### 5. Move Engine (`src/move_engine.py`)
- Main orchestrator
- Coordinates all modules
- Provides high-level API

## Development Tips

### Testing with Real Data

```python
from datetime import datetime, timedelta
from src.move_engine import MoveEngine

engine = MoveEngine()

# Use recent date for real data
recent_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# Test with well-known stocks
explanation = engine.explain_move("AAPL", recent_date)
print(explanation)
```

### Debugging

Add this to any module for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Custom Configuration

You can override default settings:

```python
from src.market_data import MarketDataFetcher

# Custom lookback period
fetcher = MarketDataFetcher(lookback_days=60)
```

## Common Issues

### Issue: "No data found for symbol"
**Solution:** Check that:
- Symbol is valid (e.g., "AAPL" not "Apple")
- Date is a trading day (not weekend/holiday)
- Date is not too recent (use at least 1 day ago)

### Issue: "OpenRouter API error"
**Solution:** Verify:
- API key is correct in `.env`
- You have API credits
- Model name is valid

### Issue: "NewsAPI rate limit"
**Solution:** 
- Free tier has 100 requests/day
- Use RSS fallback (automatic)
- Or upgrade NewsAPI plan

## Next Steps

### Enhancements to Consider:
1. Add sector classification database
2. Implement caching for API responses
3. Add more news sources
4. Create web dashboard
5. Add historical analysis
6. Support for crypto/forex
7. Real-time monitoring
8. Email/SMS alerts

## Contributing

Contributions welcome! Areas to help:
- Additional data sources
- Better sector mapping
- UI/Dashboard
- More tests
- Documentation

## Resources

- [Yahoo Finance API](https://pypi.org/project/yfinance/)
- [NewsAPI](https://newsapi.org/docs)
- [OpenRouter](https://openrouter.ai/docs)
- [FastAPI](https://fastapi.tiangolo.com/)
