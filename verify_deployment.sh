#!/bin/bash
# Quick deployment verification script

echo "🔍 Checking deployment readiness..."

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker installed"
else
    echo "❌ Docker not found - install from https://docker.com"
fi

# Check if .env exists
if [ -f "backend/.env" ]; then
    echo "✅ Backend .env file exists"
else
    echo "⚠️  Create backend/.env with your API keys"
fi

# Test Docker build
echo ""
echo "🐳 Testing Docker builds..."

cd backend
if docker build -t move-backend-test . > /dev/null 2>&1; then
    echo "✅ Backend Docker build successful"
else
    echo "❌ Backend Docker build failed"
fi
cd ..

cd frontend
if docker build -t move-frontend-test . > /dev/null 2>&1; then
    echo "✅ Frontend Docker build successful"
else
    echo "❌ Frontend Docker build failed"
fi
cd ..

echo ""
echo "📋 Next steps:"
echo "1. Choose deployment platform (see DEPLOYMENT_GUIDE.md)"
echo "2. Set up environment variables"
echo "3. Deploy!"
