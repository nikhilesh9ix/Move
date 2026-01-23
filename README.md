# AI "Why Did This Move?" Engine

A production-quality MVP that explains **WHY** stocks moved on specific dates using AI-powered post-event causal analysis.

![AI Stock Movement Explainer](https://img.shields.io/badge/AI-Stock%20Explainer-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)

## 🎯 Core Principles

- **Explanation > Prediction** - We analyze what happened, not what will happen
- **Evidence-Based Reasoning** - All conclusions backed by market data and news
- **No Trading Advice** - Informational analysis only
- **No Future Forecasting** - Historical analysis exclusively

## ✨ Features

- 📊 **Comprehensive Market Analysis** - OHLC data, volume metrics, sector/market context
- 📰 **News Integration** - Relevant headlines from NewsAPI
- 🤖 **AI-Powered Explanations** - LLaMA 3 8B via OpenRouter
- 🎨 **Modern UI** - Beautiful glassmorphism design with smooth animations
- 🔒 **Production-Ready** - Proper error handling, validation, and logging

## 🏗️ Architecture

```
Move/
├── backend/              # FastAPI backend
│   ├── services/        # Modular services
│   │   ├── market_data.py      # Yahoo Finance integration
│   │   ├── news_service.py     # NewsAPI integration
│   │   ├── ai_engine.py        # OpenRouter AI
│   │   └── evidence_builder.py # Data compilation
│   ├── main.py          # FastAPI app
│   ├── models.py        # Pydantic models
│   ├── config.py        # Configuration
│   └── requirements.txt # Python dependencies
└── frontend/            # Next.js frontend
    └── app/
        ├── page.tsx     # Main UI
        ├── layout.tsx   # Layout
        └── globals.css  # Styling
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

### 1. Get API Keys (Free)

#### NewsAPI (Required)
1. Visit [https://newsapi.org/register](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your API key (100 requests/day on free tier)

#### OpenRouter (Required)
1. Visit [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up and create an API key
3. Add credits (LLaMA 3 8B costs ~$0.0001 per request)

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and add your API keys
# NEWSAPI_KEY=your_newsapi_key_here
# OPENROUTER_API_KEY=your_openrouter_key_here
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Frontend is configured to connect to backend at http://localhost:8000
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate on macOS/Linux
uvicorn main:app --reload
```

Backend will run at: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will run at: `http://localhost:3000`

### 5. Use the Application

1. Open your browser to `http://localhost:3000`
2. Enter a stock symbol (e.g., `AAPL`, `TSLA`, `MSFT`)
3. Select a date (must be a trading day)
4. Click "Explain Movement"
5. View the AI-generated explanation!

## 📖 API Documentation

### POST `/explain`

Explains why a stock moved on a specific date.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "date": "2024-01-15"
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "date": "2024-01-15",
  "price_change_percent": 2.45,
  "explanation": "Full AI explanation...",
  "primary_driver": "Strong earnings report",
  "supporting_factors": [
    "iPhone sales exceeded expectations",
    "Services revenue growth",
    "Positive analyst upgrades"
  ],
  "move_classification": "STOCK-SPECIFIC",
  "confidence_score": 0.85,
  "uncertainty_note": null
}
```

### GET `/health`

Health check endpoint.

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **yfinance** - Yahoo Finance data (free, no API key)
- **NewsAPI** - News headlines
- **OpenRouter** - AI model access
- **Pydantic** - Data validation

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **Custom CSS** - Glassmorphism effects

### AI Model
- **LLaMA 3 8B Instruct** via OpenRouter
- Temperature: 0.2 (focused, deterministic)
- Max tokens: 600

## 🎨 UI Features

- ✨ Glassmorphism card effects
- 🌈 Gradient text and buttons
- 📊 Animated confidence score bars
- 🎯 Classification badges
- ⚡ Smooth transitions and hover effects
- 📱 Responsive design

## 🔧 Configuration

Edit `backend/.env` to customize:

```env
# API Keys
NEWSAPI_KEY=your_key
OPENROUTER_API_KEY=your_key

# AI Configuration
AI_MODEL=meta-llama/llama-3-8b-instruct
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=600

# Server Configuration
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

## 🐛 Troubleshooting

### "No data available for {symbol} on {date}"
- Ensure the date is a trading day (not weekend/holiday)
- Try a more recent date
- Verify the stock symbol is correct

### "AI service error"
- Check your OpenRouter API key is valid
- Ensure you have credits in your OpenRouter account
- Check backend logs for detailed error messages

### "Error fetching news"
- Verify your NewsAPI key is valid
- Check you haven't exceeded the free tier limit (100/day)
- News may not be available for all stocks/dates

### CORS errors
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

## 📝 Example Use Cases

- **Earnings Analysis**: "Why did AAPL move 5% on earnings day?"
- **Market Events**: "Why did tech stocks drop on Fed announcement?"
- **Sector Movements**: "Why did energy stocks rally?"
- **Individual Events**: "Why did TSLA spike on product launch?"

## ⚠️ Limitations

- **Historical Analysis Only** - No future predictions
- **Free Tier Limits** - NewsAPI: 100 requests/day
- **Trading Days Only** - No data for weekends/holidays
- **News Coverage** - Some stocks may have limited news
- **AI Accuracy** - Explanations are probabilistic, not guaranteed

## 🚫 What This Is NOT

- ❌ A trading bot
- ❌ Financial advice
- ❌ A prediction system
- ❌ Real-time analysis
- ❌ A guaranteed explanation

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🤝 Contributing

This is an MVP. Potential improvements:
- Add more data sources (earnings, SEC filings)
- Support for multiple AI models
- Historical comparison features
- Export to PDF/CSV
- User authentication
- Saved analyses

## 💡 Tips

- **Best Results**: Use dates with significant price movements (>2%)
- **Popular Stocks**: Better news coverage for large-cap stocks
- **Recent Dates**: More reliable data for recent events
- **Earnings Dates**: Particularly interesting for analysis

---

**Built with ❤️ using FastAPI, Next.js, and AI**

For questions or issues, please check the troubleshooting section above.
