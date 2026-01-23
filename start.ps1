# Write a quick start script for Windows
Write-Host "🚀 Starting AI Stock Movement Explainer..." -ForegroundColor Cyan
Write-Host ""

# Check if backend .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  No .env file found in backend directory!" -ForegroundColor Yellow
    Write-Host "Please copy backend\.env.example to backend\.env and add your API keys" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Required API keys:" -ForegroundColor Yellow
    Write-Host "  - NEWSAPI_KEY from https://newsapi.org/register" -ForegroundColor Yellow
    Write-Host "  - OPENROUTER_API_KEY from https://openrouter.ai/keys" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Start backend
Write-Host "📦 Starting Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn main:app --reload"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "🎨 Starting Frontend (Next.js)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "✅ Application starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop the servers" -ForegroundColor Yellow
