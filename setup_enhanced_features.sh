#!/bin/bash

# Enhanced Features Setup Script
# This script sets up all the new features for the AI Stock Movement Explainer

echo "🚀 Setting up Enhanced Features for AI Stock Movement Explainer"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "ENHANCED_FEATURES.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo ""
echo "📦 Step 1: Installing Backend Dependencies"
echo "-------------------------------------------"
cd backend || exit

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install requirements
echo "Installing Python packages..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed"

# Download TextBlob corpora
echo ""
echo "📚 Step 2: Downloading TextBlob Language Data"
echo "----------------------------------------------"
python3 -m textblob.download_corpora

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: TextBlob corpora download failed. Sentiment analysis may not work."
else
    echo "✅ TextBlob corpora downloaded"
fi

# Verify TextBlob installation
echo ""
echo "🔍 Step 3: Verifying Sentiment Analysis"
echo "---------------------------------------"
python3 -c "from textblob import TextBlob; print('✅ TextBlob is working correctly!')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: TextBlob verification failed"
else
    echo "✅ Sentiment analysis ready"
fi

# Check for .env file
echo ""
echo "🔐 Step 4: Checking Environment Configuration"
echo "---------------------------------------------"
cd ..
if [ -f "backend/.env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  Warning: .env file not found"
    echo "   Create backend/.env with your API keys:"
    echo "   NEWSAPI_KEY=your_key_here"
    echo "   OPENROUTER_API_KEY=your_key_here"
fi

# Frontend setup
echo ""
echo "🎨 Step 5: Verifying Frontend Dependencies"
echo "------------------------------------------"
cd Move/frontend || exit

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Warning: Node.js is not installed"
    echo "   Please install Node.js to run the frontend"
else
    echo "✅ Node.js found: $(node --version)"
    
    # Check if node_modules exists
    if [ -d "node_modules" ]; then
        echo "✅ Frontend dependencies already installed"
    else
        echo "Installing frontend dependencies..."
        npm install
        if [ $? -ne 0 ]; then
            echo "❌ Error: Failed to install frontend dependencies"
            exit 1
        fi
        echo "✅ Frontend dependencies installed"
    fi
    
    # Verify recharts is installed
    if npm list recharts &> /dev/null; then
        echo "✅ Recharts library found"
    else
        echo "⚠️  Warning: Recharts not found, installing..."
        npm install recharts
    fi
fi

cd ../..

# Summary
echo ""
echo "=============================================================="
echo "✅ Setup Complete!"
echo "=============================================================="
echo ""
echo "📋 What's New:"
echo "  ✅ Historical Price Chart Visualization"
echo "  ✅ Sector & Market Context Analysis"
echo "  ✅ Enhanced News Integration with Sentiment"
echo "  ✅ Multi-Day Movement Analysis"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Start the backend server:"
echo "   cd backend"
echo "   uvicorn main:app --reload"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd Move/frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "  - ENHANCED_FEATURES.md - Complete feature documentation"
echo "  - QUICK_START.md - Usage guide and examples"
echo "  - IMPLEMENTATION_CHECKLIST.md - Verification checklist"
echo ""
echo "🎉 Happy analyzing!"
