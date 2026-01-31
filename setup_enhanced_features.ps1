# Enhanced Features Setup Script for Windows
# This script sets up all the new features for the AI Stock Movement Explainer

Write-Host "🚀 Setting up Enhanced Features for AI Stock Movement Explainer" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "ENHANCED_FEATURES.md")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Step 1: Installing Backend Dependencies" -ForegroundColor Yellow
Write-Host "-------------------------------------------" -ForegroundColor Yellow

# Navigate to backend
Set-Location backend

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

$pythonVersion = & $pythonCmd.Name --version
Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green

# Install requirements
Write-Host "Installing Python packages..." -ForegroundColor Yellow
& $pythonCmd.Name -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Python dependencies installed" -ForegroundColor Green

# Download TextBlob corpora
Write-Host ""
Write-Host "📚 Step 2: Downloading TextBlob Language Data" -ForegroundColor Yellow
Write-Host "----------------------------------------------" -ForegroundColor Yellow
& $pythonCmd.Name -m textblob.download_corpora

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: TextBlob corpora download failed. Sentiment analysis may not work." -ForegroundColor Yellow
} else {
    Write-Host "✅ TextBlob corpora downloaded" -ForegroundColor Green
}

# Verify TextBlob installation
Write-Host ""
Write-Host "🔍 Step 3: Verifying Sentiment Analysis" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow

$testResult = & $pythonCmd.Name -c "from textblob import TextBlob; print('✅ TextBlob is working correctly!')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Warning: TextBlob verification failed" -ForegroundColor Yellow
} else {
    Write-Host $testResult -ForegroundColor Green
}

# Check for .env file
Write-Host ""
Write-Host "🔐 Step 4: Checking Environment Configuration" -ForegroundColor Yellow
Write-Host "---------------------------------------------" -ForegroundColor Yellow

Set-Location ..
if (Test-Path "backend\.env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "   Create backend\.env with your API keys:" -ForegroundColor Yellow
    Write-Host "   NEWSAPI_KEY=your_key_here" -ForegroundColor Gray
    Write-Host "   OPENROUTER_API_KEY=your_key_here" -ForegroundColor Gray
}

# Frontend setup
Write-Host ""
Write-Host "🎨 Step 5: Verifying Frontend Dependencies" -ForegroundColor Yellow
Write-Host "------------------------------------------" -ForegroundColor Yellow

Set-Location Move\frontend

# Check if Node.js is installed
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue

if (-not $nodeCmd) {
    Write-Host "⚠️  Warning: Node.js is not installed" -ForegroundColor Yellow
    Write-Host "   Please install Node.js to run the frontend" -ForegroundColor Yellow
} else {
    $nodeVersion = & node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    
    # Check if node_modules exists
    if (Test-Path "node_modules") {
        Write-Host "✅ Frontend dependencies already installed" -ForegroundColor Green
    } else {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Error: Failed to install frontend dependencies" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    }
    
    # Verify recharts is installed
    $rechartsCheck = npm list recharts 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Recharts library found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Warning: Recharts not found, installing..." -ForegroundColor Yellow
        npm install recharts
    }
}

Set-Location ..\..

# Summary
Write-Host ""
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 What's New:" -ForegroundColor Cyan
Write-Host "  ✅ Historical Price Chart Visualization" -ForegroundColor Green
Write-Host "  ✅ Sector & Market Context Analysis" -ForegroundColor Green
Write-Host "  ✅ Enhanced News Integration with Sentiment" -ForegroundColor Green
Write-Host "  ✅ Multi-Day Movement Analysis" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the backend server:" -ForegroundColor Yellow
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   uvicorn main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "2. In a new terminal, start the frontend:" -ForegroundColor Yellow
Write-Host "   cd Move\frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open your browser to:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "  - ENHANCED_FEATURES.md - Complete feature documentation" -ForegroundColor Gray
Write-Host "  - QUICK_START.md - Usage guide and examples" -ForegroundColor Gray
Write-Host "  - IMPLEMENTATION_CHECKLIST.md - Verification checklist" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Happy analyzing!" -ForegroundColor Magenta
