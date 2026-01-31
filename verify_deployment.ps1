# Quick deployment verification script for Windows

Write-Host "🔍 Checking deployment readiness..." -ForegroundColor Cyan

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker installed" -ForegroundColor Green
} else {
    Write-Host "❌ Docker not found - install from https://docker.com" -ForegroundColor Red
}

# Check if .env exists
if (Test-Path "backend\.env") {
    Write-Host "✅ Backend .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Create backend\.env with your API keys" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Deployment options:" -ForegroundColor Cyan
Write-Host "1. Vercel (Frontend) + Railway (Backend) - Easiest, free tier available"
Write-Host "2. Render.com - All-in-one, free tier available"
Write-Host "3. Docker - Local testing or cloud deployment"
Write-Host "4. Fly.io - Global edge deployment"
Write-Host ""
Write-Host "📖 See DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Green
