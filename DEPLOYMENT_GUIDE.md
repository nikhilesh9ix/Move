# 🚀 Deployment Guide for AI Stock Movement Explainer

This guide covers multiple deployment options for your application. Choose the one that best fits your needs.

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ API Keys ready (NewsAPI, OpenRouter)
- ✅ GitHub repository up to date (already done!)
- ✅ Node.js 18+ installed locally (for testing)
- ✅ Python 3.12 installed locally (for testing)

---

## 🎯 Recommended Deployment Options

### **Option 1: Vercel (Frontend) + Railway (Backend) - EASIEST** ⭐

Best for: Quick deployment with minimal configuration

#### Deploy Backend to Railway:

1. **Go to [Railway.app](https://railway.app)**
   - Sign up/login with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `nikhilesh9ix/Move`

3. **Configure Backend Service**
   - Railway will auto-detect the Dockerfile
   - Add environment variables:
     ```
     NEWSAPI_KEY=your_newsapi_key
     OPENROUTER_API_KEY=your_openrouter_key
     FRONTEND_URL=https://your-app.vercel.app
     PORT=8000
     ```

4. **Deploy**
   - Railway will automatically build and deploy
   - Copy your backend URL (e.g., `https://move-backend.railway.app`)

#### Deploy Frontend to Vercel:

1. **Go to [Vercel.com](https://vercel.com)**
   - Sign up/login with GitHub

2. **Import Project**
   - Click "Add New Project"
   - Import `nikhilesh9ix/Move`
   - Set root directory to `frontend`

3. **Configure Build Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

4. **Add Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://move-backend.railway.app
   ```

5. **Deploy**
   - Click "Deploy"
   - Your app will be live at `https://your-app.vercel.app`

---

### **Option 2: Render.com - ALL-IN-ONE** 🎨

Best for: Single platform deployment

1. **Go to [Render.com](https://render.com)**
   - Sign up/login with GitHub

2. **Create New Blueprint**
   - Click "New" → "Blueprint"
   - Connect your `nikhilesh9ix/Move` repository
   - Render will detect `render.yaml`

3. **Configure Environment Variables**
   - Add these secrets in Render dashboard:
     ```
     NEWSAPI_KEY=your_newsapi_key
     OPENROUTER_API_KEY=your_openrouter_key
     ```

4. **Deploy**
   - Render will create both services automatically
   - Frontend: `https://move-frontend.onrender.com`
   - Backend: `https://move-backend.onrender.com`

⚠️ **Note**: Free tier services sleep after 15 minutes of inactivity (first request may be slow)

---

### **Option 3: Docker (Local or Cloud)** 🐳

Best for: Full control, cloud-agnostic deployment

#### Local Development:

```powershell
# Make sure you're in the project root
cd C:\Files\Files\Portfolio\Projects\Move

# Create .env file in backend directory with your API keys
# (or copy from existing .env)

# Build and run with Docker Compose
docker-compose up --build

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Deploy to Cloud (AWS/GCP/Azure):

**Docker Hub (Recommended first step):**

```powershell
# Build and tag images
docker build -t yourusername/move-backend:latest ./backend
docker build -t yourusername/move-frontend:latest ./frontend

# Push to Docker Hub
docker push yourusername/move-backend:latest
docker push yourusername/move-frontend:latest
```

**Then deploy to:**
- **AWS ECS/Fargate**: Use the Docker images
- **Google Cloud Run**: Deploy containers directly
- **Azure Container Apps**: Import from Docker Hub

---

### **Option 4: Fly.io** 🪰

Best for: Global edge deployment

1. **Install Fly CLI**
   ```powershell
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login and Initialize**
   ```powershell
   fly auth login
   
   # Deploy Backend
   cd backend
   fly launch --name move-backend
   fly secrets set NEWSAPI_KEY=your_key OPENROUTER_API_KEY=your_key
   fly deploy
   
   # Deploy Frontend
   cd ../frontend
   fly launch --name move-frontend
   fly secrets set NEXT_PUBLIC_API_URL=https://move-backend.fly.dev
   fly deploy
   ```

---

## 🔧 Environment Variables Reference

### Backend (.env):
```env
NEWSAPI_KEY=your_newsapi_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
FRONTEND_URL=https://your-frontend-url.com
```

### Frontend:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## 🧪 Testing Your Deployment

After deployment, test all features:

1. **Basic Functionality**
   - Visit your frontend URL
   - Enter stock symbol (e.g., AAPL)
   - Select a date
   - Click "Analyze"

2. **All Tabs Working**
   - ✅ Overview tab shows explanation
   - ✅ Charts tab displays price/volume
   - ✅ Sector tab shows market context
   - ✅ News tab displays sentiment analysis
   - ✅ Trends tab shows multi-day patterns

3. **API Health Check**
   - Visit `your-backend-url/docs`
   - Should see Swagger UI with all endpoints

---

## 🔍 Troubleshooting

### Frontend can't connect to backend:
- ✅ Check `NEXT_PUBLIC_API_URL` matches your backend URL
- ✅ Verify backend is running (visit `/docs`)
- ✅ Check CORS settings in `backend/main.py`

### Backend errors:
- ✅ Verify environment variables are set correctly
- ✅ Check API keys are valid
- ✅ View logs in your platform's dashboard

### Build failures:
- ✅ Ensure Node.js version is 18+ for frontend
- ✅ Ensure Python version is 3.12 for backend
- ✅ Check `requirements.txt` and `package.json` are complete

---

## 💰 Cost Comparison

| Platform | Backend | Frontend | Total/Month |
|----------|---------|----------|-------------|
| **Vercel + Railway** | Free tier | Free tier | $0 (with limits) |
| **Render** | Free tier | Free tier | $0 (with limits) |
| **Fly.io** | Free tier | Free tier | $0 (with limits) |
| **AWS** | ~$10-20 | ~$5 | ~$15-25 |
| **Heroku** | $7 | $7 | $14 |

---

## 🎉 Quick Start (Copy-Paste Ready)

**Fastest deployment (Vercel + Railway):**

1. Railway Backend:
   - Go to railway.app → New Project → Deploy from GitHub
   - Select your repo → Add env vars → Deploy
   
2. Vercel Frontend:
   - Go to vercel.com → New Project → Import from GitHub
   - Select your repo → Set root to `frontend` → Add `NEXT_PUBLIC_API_URL` → Deploy

**Done! Your app is live in ~5 minutes.** 🚀

---

## 📚 Next Steps

After deployment:
- [ ] Set up custom domain
- [ ] Configure monitoring/alerts
- [ ] Set up CI/CD for automatic deployments
- [ ] Add analytics (Vercel Analytics, Google Analytics)
- [ ] Set up error tracking (Sentry)
- [ ] Configure rate limiting for API

---

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Render Docs: https://render.com/docs
- Docker Docs: https://docs.docker.com

Happy Deploying! 🎊
