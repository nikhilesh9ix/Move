# Move v4

Move v4 is a full-stack stock movement intelligence app that explains *why* stocks and portfolios moved using a multi-agent backend pipeline and a real-time dashboard UI.

It combines:
- FastAPI for APIs + WebSocket streaming
- A modular agent pipeline for market data, attribution, and explanations
- Next.js for an interactive frontend dashboard
- Live polling and event broadcasting for real-time updates

---

## Table of Contents

- [Move v4](#move-v4)
  - [Table of Contents](#table-of-contents)
  - [What It Does](#what-it-does)
  - [Architecture](#architecture)
    - [High-level flow](#high-level-flow)
    - [Backend agent pipeline](#backend-agent-pipeline)
  - [Tech Stack](#tech-stack)
    - [Backend](#backend)
    - [Frontend](#frontend)
  - [Project Structure](#project-structure)
  - [Run Locally](#run-locally)
    - [1) Start backend (Terminal 1)](#1-start-backend-terminal-1)
    - [2) Start frontend (Terminal 2)](#2-start-frontend-terminal-2)
  - [API Reference](#api-reference)
    - [Health](#health)
    - [Analyze stock move](#analyze-stock-move)
    - [Portfolio summary](#portfolio-summary)
    - [Daily why card](#daily-why-card)
  - [WebSocket Events](#websocket-events)
  - [How The Pipeline Works](#how-the-pipeline-works)
  - [Data Sources and Fallbacks](#data-sources-and-fallbacks)
  - [Troubleshooting](#troubleshooting)
    - [Frontend shows backend offline warning](#frontend-shows-backend-offline-warning)
    - [WebSocket not connecting](#websocket-not-connecting)
    - [Empty or stale market/news values](#empty-or-stale-marketnews-values)
    - [Python package errors](#python-package-errors)
  - [Future Improvements](#future-improvements)

---

## What It Does

- Shows daily portfolio-level explanations (Why Card)
- Summarizes total portfolio performance with top gainers/losers
- Lets users analyze any stock on a specific date
- Streams live analysis updates when price movement crosses a threshold
- Displays attribution factors (market/sector/macro/rates/earnings, etc.) with confidence

---

## Architecture

### High-level flow

1. Frontend calls FastAPI REST endpoints for initial page data
2. Frontend subscribes to `/ws/updates` for real-time events
3. Background `PriceWatcher` polls watched tickers every 20 seconds
4. If movement exceeds threshold (`±0.8%`), backend runs full analysis pipeline
5. Result is cached in event store and broadcast to all connected clients

### Backend agent pipeline

- `MarketDataAgent` -> fetches normalized `PriceData`
- `CausalInferenceAgent` -> computes factor attribution
- `ExplanationAgent` -> generates human-readable explanation + insights

Orchestration lives in `move_backend/services/orchestrator.py`.

---

## Tech Stack

### Backend

- Python (FastAPI)
- Uvicorn (ASGI server)
- Pydantic v2 models
- yfinance (live market + news fetch)

### Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion
- Recharts
- Axios

---

## Project Structure

```text
move_backend/
  main.py
  agents/
  core/
  data/
  models/
  routes/
  services/

move_frontend/
  src/
    app/
    components/
    constants/
    hooks/
    services/
    types/
```

---

## Run Locally

### 1) Start backend (Terminal 1)

```powershell
cd move_backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install fastapi uvicorn[standard] pydantic yfinance
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2) Start frontend (Terminal 2)

```powershell
cd move_frontend
npm install
npm run dev
```

Frontend will be available at:
- `http://localhost:3000`

The frontend is configured to proxy `/move-api/*` to `http://localhost:8000/*`.

---

## API Reference

Base URL: `http://localhost:8000`

### Health

- `GET /health`

Returns backend health, connected WebSocket clients, and cached tickers.

### Analyze stock move

- `POST /analyze-move`

Request body:

```json
{
  "stock": "TCS",
  "date": "2026-04-20"
}
```

Response shape:

```json
{
  "stock": "TCS",
  "price_change": 1.23,
  "attribution": [{ "factor": "sector", "contribution": 42.1 }],
  "explanation": "...",
  "historical_hint": "...",
  "actionable_insight": "...",
  "confidence_pct": 74
}
```

### Portfolio summary

- `GET /portfolio-summary?date=2026-04-20`

Returns total portfolio value/change plus top gainers/losers.

### Daily why card

- `GET /daily-why-card?date=2026-04-20`

Returns top portfolio causes, confidence, and summary explanation.

---

## WebSocket Events

Endpoint: `ws://localhost:8000/ws/updates`

On connect, server sends:

```json
{
  "type": "connected",
  "message": "Connected to Move real-time feed",
  "initial_events": {
    "TCS": {
      "type": "analysis_update",
      "ticker": "TCS",
      "timestamp": "2026-04-20T11:20:01",
      "price_change": 1.6,
      "attribution": [{ "factor": "sector", "contribution": 35.0 }],
      "explanation": "..."
    }
  }
}
```

Server also emits:
- `analysis_update` when threshold is crossed
- `heartbeat` every 30s (when clients are connected)
- `pong` in response to client `ping`

---

## How The Pipeline Works

1. `run_analysis(stock, date)` fetches market + news data in parallel
2. Causal attribution is computed from price/news signal
3. Explanation text and confidence are generated
4. API returns a typed `AnalyzeResponse`

Portfolio-level flow:
- `run_portfolio_summary(date)` computes weighted holding changes
- `run_why_card(date)` aggregates per-holding factors into top portfolio causes

---

## Data Sources and Fallbacks

- Primary source: yfinance (prices and news)
- Built-in resilience:
  - price fetch timeout protection
  - TTL caching for price/news/change polling
  - deterministic mock fallback when live data is unavailable

This keeps the UI responsive even with external data-source delays.

---

## Troubleshooting

### Frontend shows backend offline warning

- Ensure backend is running on port `8000`
- Check `http://localhost:8000/health`

### WebSocket not connecting

- Ensure backend is running and `ws://localhost:8000/ws/updates` is reachable
- Verify no firewall/proxy is blocking local WebSocket traffic

### Empty or stale market/news values

- yfinance can intermittently fail or rate-limit
- The app falls back to mock data automatically

### Python package errors

Install/upgrade required backend packages:

```powershell
pip install --upgrade fastapi "uvicorn[standard]" pydantic yfinance
```

---

## Future Improvements

- Add `requirements.txt` or `pyproject.toml` for reproducible backend setup
- Add test suites for agents/routes/services
- Add environment-based configuration for intervals/thresholds
- Add Docker and docker-compose for one-command startup
- Add CI checks (lint, test, type checks)
