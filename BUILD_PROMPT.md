# Prompt to Build "Move" - AI Stock Movement Explainer

## Project Overview

Build a production-quality full-stack web application called **"Move"** that explains **WHY** stocks moved on specific dates using AI-powered post-event causal analysis. This is NOT a prediction tool - it's an evidence-based explanation engine for historical stock movements.

## Core Principles

1. **Explanation > Prediction** - Analyze what happened, never predict the future
2. **Evidence-Based Reasoning** - All conclusions backed by market data and news
3. **No Trading Advice** - Informational analysis only
4. **No Future Forecasting** - Historical analysis exclusively

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.10+
- **Key Libraries**:
  - `uvicorn[standard]` 0.27.0 - ASGI server
  - `requests` 2.31.0 - HTTP requests
  - `python-dotenv` 1.0.0 - Environment management
  - `pydantic` 2.5.3 - Data validation
  - `pydantic-settings` 2.1.0 - Settings management

### Frontend
- **Framework**: Next.js 14.1.0
- **Language**: TypeScript 5.3.3
- **UI Libraries**:
  - React 18.2.0
  - Tailwind CSS 3.4.1
  - Framer Motion 11.0.3 - Animations
  - Lucide React 0.312.0 - Icons
  - Recharts 2.10.4 - Data visualization
  - date-fns 3.2.0 - Date handling
- **Utilities**:
  - `class-variance-authority` - Component variants
  - `clsx` + `tailwind-merge` - Class name management

### External APIs
- **Yahoo Finance** - Market data (via yfinance, free)
- **NewsAPI** - News headlines (free tier: 100 requests/day)
- **OpenRouter** - AI explanations using LLaMA 3 8B (~$0.0001 per request)

## Project Structure

```
Move/
├── backend/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── market_data.py      # Yahoo Finance integration
│   │   ├── news_service.py     # NewsAPI integration
│   │   ├── ai_engine.py        # OpenRouter AI with LLaMA 3
│   │   ├── evidence_builder.py # Compile market + news data
│   │   └── alphavantage_service.py # Alternative data source
│   ├── main.py                 # FastAPI app + routes
│   ├── models.py               # Pydantic models
│   ├── config.py               # Settings from .env
│   ├── demo.py                 # Demo endpoint
│   ├── requirements.txt
│   └── .env                    # API keys (not committed)
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main page with hero + search
│   │   ├── layout.tsx          # Root layout + theme provider
│   │   └── globals.css         # Global styles + animations
│   ├── components/
│   │   ├── ui/                 # Reusable components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Badge.tsx
│   │   ├── theme/              # Dark/light mode
│   │   │   ├── ThemeProvider.tsx
│   │   │   └── ThemeToggle.tsx
│   │   ├── features/           # Feature components
│   │   │   ├── StockSearch.tsx
│   │   │   ├── AnalysisResults.tsx
│   │   │   └── ShowcasePage.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       └── ClientLayout.tsx
│   ├── lib/
│   │   └── utils.ts            # Utility functions (cn)
│   ├── tailwind.config.js      # Tailwind configuration
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── postcss.config.js
├── README.md
├── DEVELOPMENT.md
└── start.ps1                   # Startup script
```

## Backend Implementation Details

### 1. Configuration (config.py)

Create a settings class using Pydantic Settings that loads from `.env`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    newsapi_key: str
    openrouter_api_key: str
    ai_model: str = "meta-llama/llama-3-8b-instruct"
    ai_temperature: float = 0.2
    ai_max_tokens: int = 600
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### 2. Data Models (models.py)

Define Pydantic models for request/response validation:

**ExplainRequest:**
- `symbol`: str (1-10 chars)
- `date`: str (YYYY-MM-DD format, validated with regex pattern)

**ExplainResponse:**
- `symbol`: str
- `date`: str
- `price_change_percent`: float
- `explanation`: str (main narrative)
- `primary_driver`: str
- `supporting_factors`: List[str]
- `move_classification`: str (e.g., "Moderate Increase")
- `confidence_score`: float
- `uncertainty_note`: Optional[str]

### 3. Market Data Service (services/market_data.py)

Use `yfinance` library to fetch:
- OHLC data (Open, High, Low, Close)
- Volume
- Price change percentage
- Multi-day context (3 days before, target day, 3 days after)

Return structured dictionary with:
- `date`, `open`, `high`, `low`, `close`, `volume`
- `price_change_percent`
- `previous_close`
- `volume_vs_avg` (if available)

### 4. News Service (services/news_service.py)

Integrate NewsAPI to fetch relevant headlines:
- Search by stock symbol + company name
- Date range: 3 days before to target date
- Filter and rank by relevance
- Return list of dictionaries with: `title`, `source`, `publishedAt`, `description`

### 5. Evidence Builder (services/evidence_builder.py)

Compile market data + news into a structured text format for AI:
```
=== MARKET DATA ===
Date: {date}
Price Movement: {price_change_percent}%
Open: ${open} | Close: ${close}
Volume: {volume:,}

=== NEWS & EVENTS ===
[List top 5-10 relevant headlines with dates]

=== MARKET CONTEXT ===
[3-day price history before/after]
```

### 6. AI Engine (services/ai_engine.py)

Use OpenRouter API to call LLaMA 3 8B:

**System Prompt:**
```
You are a financial analyst providing evidence-based explanations for stock price movements. 
You NEVER make predictions or give trading advice. 
You only analyze what happened based on provided evidence.
```

**User Prompt Structure:**
```
Analyze why {symbol} moved {price_change_percent}% on {date}.

Evidence:
{compiled_evidence}

Provide:
1. EXPLANATION: 2-3 paragraph narrative
2. PRIMARY DRIVER: Main cause in one sentence
3. SUPPORTING FACTORS: 2-4 bullet points
4. MOVE CLASSIFICATION: (e.g., "Moderate Increase", "Significant Drop")
5. CONFIDENCE SCORE: 0.0-1.0
6. UNCERTAINTY NOTE: If data is limited
```

Parse the AI response and extract structured components.

### 7. FastAPI Application (main.py)

**Endpoints:**

`GET /` - Health check

`POST /explain` - Main analysis endpoint
- Accept `ExplainRequest`
- Orchestrate all services:
  1. Fetch market data
  2. Fetch news
  3. Build evidence
  4. Generate AI explanation
- Return `ExplainResponse`

**CORS Middleware:**
- Allow origins: `http://localhost:3000`, `http://localhost:3001`
- Allow all methods and headers

**Error Handling:**
- 404 for invalid symbols/dates
- 500 for API failures
- Proper logging throughout

### 8. Demo Endpoint (demo.py)

Create a router with `GET /demo/explain` that returns a pre-generated example (e.g., AAPL on a specific date) without requiring input.

## Frontend Implementation Details

### Design System

**Theme: Cyber Finance Noir + Bloomberg Professional**

**Colors:**
- Primary: Indigo (`#6366f1`)
- Success/Positive: Emerald/Green
- Error/Negative: Red
- Dark mode: Dark navy background (`#0A0E27`) with neon cyan accents (`#00F5FF`)
- Light mode: Clean white with subtle indigo gradients

**Typography:**
- Sans: Inter
- Display: Orbitron/Space Grotesk
- Mono: JetBrains Mono

**Font Sizes:**
- Display XL: 72px
- Display LG: 56px
- H1: 48px
- H2: 36px
- H3: 30px
- Body: 16px
- Small: 14px

### Component Architecture

#### 1. UI Components (components/ui/)

**Button.tsx** - Using `class-variance-authority`:
- Variants: `default`, `outline`, `ghost`
- Sizes: `sm`, `md`, `lg`
- States: hover, active, disabled
- Support for icons

**Card.tsx**:
- Glassmorphism effect (backdrop-blur, semi-transparent background)
- Border glow on hover
- Shadow depth variations

**Input.tsx**:
- Focus ring with brand color
- Error states
- Icon support (left/right)

**Badge.tsx**:
- Color variants: success, error, warning, info
- Sizes: sm, md, lg

#### 2. Theme System (components/theme/)

**ThemeProvider.tsx**:
- Context-based dark/light mode
- Persist preference in localStorage
- System preference detection

**ThemeToggle.tsx**:
- Animated sun/moon icon toggle
- Smooth transitions

#### 3. Feature Components (components/features/)

**StockSearch.tsx**:
- Symbol input (uppercase, max 10 chars)
- Date picker (max: today, default: yesterday)
- Validation before submission
- Loading state
- Emit `onSearch(symbol, date)` event

**AnalysisResults.tsx**:
- Display full analysis in cards:
  - Header: Symbol, date, price change (colored badge)
  - Explanation narrative (main card)
  - Primary driver (highlighted)
  - Supporting factors (bullet list)
  - Classification + confidence (badges)
  - Uncertainty note (if present)
- Smooth fade-in animation
- Responsive grid layout

**ShowcasePage.tsx** (optional):
- Demo pre-loaded examples
- Quick-start templates

#### 4. Layout Components

**Header.tsx**:
- Logo/title
- Theme toggle
- Sticky on scroll with backdrop blur

**ClientLayout.tsx**:
- Wrap children with ThemeProvider
- Apply global container

### Main Page (app/page.tsx)

**Hero Section:**
- Large headline: "Understand Why **Stocks Move**" (gradient text)
- Subheadline: "Evidence-based AI analysis..."
- Feature cards grid:
  - Data-Driven (Database icon)
  - AI-Powered (Sparkles icon)
  - Transparent (Shield icon)
- Background: Gradient orbs with blur

**Search Section:**
- StockSearch component
- Error message display
- Loading spinner

**Results Section:**
- Conditional rendering based on state
- AnalysisResults component when data available
- Error card when failed

### Styling (globals.css)

**Animations:**
```css
@keyframes fade-in { ... }
@keyframes slide-up { ... }
@keyframes gradient-shift { ... }

.animate-fade-in { animation: fade-in 0.6s ease-out; }
.animate-slide-up { animation: slide-up 0.8s ease-out; }
.gradient-text { 
  background: linear-gradient(to right, indigo, purple);
  -webkit-background-clip: text;
  color: transparent;
}
```

**Glass Effect:**
```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Tailwind Configuration (tailwind.config.js)

Extend theme with:
- Custom colors (cyber, neon palettes)
- Custom font families
- Custom font sizes (display-xl, display-lg, etc.)
- Custom animations
- Container max-width: 1280px

### API Integration

Use `fetch` API to call backend:
```typescript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const response = await fetch(`${apiUrl}/explain`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol, date })
})
```

Handle errors:
- Network errors (backend not running)
- 404 (invalid symbol)
- 500 (server error)
- Display user-friendly messages

## Features to Implement

### Core Features

1. **Stock Analysis**
   - Search any stock by symbol
   - Select any historical date
   - View comprehensive analysis

2. **Evidence Display**
   - Price movement visualization
   - News headlines integration
   - Market context (before/after)

3. **AI Explanation**
   - Natural language narrative
   - Structured breakdown
   - Confidence scoring
   - Uncertainty transparency

4. **Responsive Design**
   - Mobile-friendly
   - Tablet optimized
   - Desktop-first professional layout

5. **Dark/Light Mode**
   - System preference detection
   - Manual toggle
   - Persistent preference

### UX Enhancements

1. **Loading States**
   - Skeleton screens
   - Progress indicators
   - Smooth transitions

2. **Error Handling**
   - Friendly error messages
   - Retry options
   - Helpful guidance (e.g., "Backend not running?")

3. **Animations**
   - Page load animations
   - Component transitions
   - Hover effects
   - Scroll reveals

4. **Accessibility**
   - ARIA labels
   - Keyboard navigation
   - Focus management
   - Screen reader support

## Environment Configuration

### Backend (.env)

```env
NEWSAPI_KEY=your_newsapi_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
AI_MODEL=meta-llama/llama-3-8b-instruct
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=600
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

### Setup Instructions

1. **Get API Keys:**
   - NewsAPI: https://newsapi.org/register (free tier)
   - OpenRouter: https://openrouter.ai/keys (add $5 credits)

2. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   # Create .env and add API keys
   uvicorn main:app --reload
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testing

**Backend:**
- Test individual services (market_data, news, ai_engine)
- Test demo endpoint: `GET /demo/explain`
- Test main endpoint: `POST /explain`

**Frontend:**
- Test search form validation
- Test API integration
- Test error states
- Test dark/light mode
- Test responsive layouts

## Production Considerations

### Backend

1. **Rate Limiting**
   - Implement rate limits for API endpoints
   - Cache market data (same stock/date)

2. **Error Logging**
   - Structured logging
   - Error tracking (Sentry)

3. **Security**
   - Input validation
   - API key protection
   - CORS restrictions

### Frontend

1. **Performance**
   - Code splitting
   - Image optimization
   - Lazy loading

2. **SEO**
   - Meta tags
   - Open Graph tags
   - Semantic HTML

3. **Analytics**
   - Usage tracking
   - Error monitoring

## Documentation Requirements

Create the following files:

1. **README.md** - Project overview, setup, features
2. **DEVELOPMENT.md** - Development guide, architecture
3. **DESIGN_SYSTEM.md** - Design specifications, component library
4. **SETUP_GUIDE.md** - Step-by-step setup instructions
5. **start.ps1** - PowerShell startup script (Windows)

## Key Constraints & Rules

1. **NO PREDICTIONS**: Never forecast future prices or give trading advice
2. **EVIDENCE ONLY**: Base all conclusions on provided data
3. **TRANSPARENCY**: Always show confidence scores and uncertainty
4. **HISTORICAL**: Only analyze past events, never future
5. **EDUCATIONAL**: Position as learning/analysis tool, not trading tool

## Success Criteria

The project is complete when:

1. ✅ User can search any stock symbol + date
2. ✅ Backend fetches market data from Yahoo Finance
3. ✅ Backend fetches news from NewsAPI
4. ✅ AI generates evidence-based explanation via OpenRouter
5. ✅ Frontend displays results in beautiful, responsive UI
6. ✅ Dark/light mode works correctly
7. ✅ Error states handled gracefully
8. ✅ Loading states smooth and informative
9. ✅ No predictions or trading advice anywhere
10. ✅ Professional Bloomberg-grade appearance

## Example Analysis Output

**Input:** AAPL, 2024-08-01

**Output:**
- **Price Change:** +2.3%
- **Explanation:** "Apple Inc. (AAPL) experienced a moderate increase of 2.3% on August 1, 2024. This movement was primarily driven by positive earnings surprises announced the previous day, where the company beat analyst expectations on both revenue and EPS. Additionally, the broader tech sector showed strength, with the NASDAQ gaining 1.8% on the same day..."
- **Primary Driver:** "Strong Q2 earnings beat with revenue up 8% YoY"
- **Supporting Factors:**
  - Tech sector momentum (NASDAQ +1.8%)
  - Positive analyst upgrades from major firms
  - Services revenue growth exceeded expectations
- **Classification:** "Moderate Increase"
- **Confidence:** 0.82
- **Uncertainty:** "News coverage was limited; some factors may be inferred from broader market context"

---

## Final Notes

This is a **production-quality MVP**, not a prototype. Focus on:
- Clean, maintainable code
- Professional UI/UX
- Robust error handling
- Clear documentation
- Evidence-based analysis (never predictions)

The goal is to create a tool that helps users **understand market movements** through AI-powered analysis of historical data, positioned as an educational and informational resource.
