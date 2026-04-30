# Deploy Move to Hugging Face Spaces

## Overview

This guide walks you through deploying the Move v4 full-stack application to Hugging Face Spaces for free.

**What will be deployed:**
- ✅ FastAPI backend (Python) on internal port 8000
- ✅ Next.js frontend on port 7860
- ✅ Nginx reverse proxy handling both services
- ✅ WebSocket real-time updates
- ✅ All agent pipelines and market data fetching

**Cost:** Completely free (HF Spaces free tier)

---

## Prerequisites

1. **GitHub Account** - Push your code to GitHub
2. **Hugging Face Account** - Create at https://huggingface.co
3. **Git installed** - For version control

---

## Step 1: Push Code to GitHub

Make sure your Move project is in a GitHub repository:

```bash
cd "c:\Files\Files\Portfolio\Projects\Move v4"
git init
git add .
git commit -m "Initial Move v4 commit"
git remote add origin https://github.com/YOUR_USERNAME/Move.git
git branch -M main
git push -u origin main
```

✅ **All deployment files are already created:**
- `Dockerfile` - Multi-stage build for full stack
- `nginx.conf` - Reverse proxy configuration
- `.dockerignore` - Build optimization

---

## Step 2: Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name:** `move-app` (or your choice)
   - **License:** Select one (e.g., "Open RAIL License")
   - **Space SDK:** Select **"Docker"**
   - **Space hardware:** Free CPU (default)
   - **Visibility:** Public or Private

3. Click **"Create space"**

---

## Step 3: Connect Your GitHub Repository

After creating the space, you'll see setup instructions. Connect your GitHub repo:

### Option A: Using HF CLI (Easiest)

```bash
# Install Hugging Face CLI
pip install huggingface-hub

# Login
huggingface-cli login

# Push to your HF Space
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/move-app
git push huggingface main
```

### Option B: Manual Git Setup

```bash
# Add HF Space as remote
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/move-app

# Push code
git push huggingface main
```

HF will automatically:
- ✅ Detect the Dockerfile
- ✅ Build the Docker image
- ✅ Deploy the container
- ✅ Expose the app at: `https://huggingface.co/spaces/YOUR_USERNAME/move-app`

---

## Step 4: Monitor Deployment

1. Go to your Space URL
2. Click the **"Logs"** tab to watch the build process
3. Wait for: "Build successful" ✅

**Build typically takes 5-10 minutes** (first build is slower due to dependencies)

---

## Step 5: Access Your App

Once deployed, your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/move-app
```

**Testing:**
- ✅ Frontend loads at the main URL
- ✅ WebSocket connects automatically (real-time updates)
- ✅ Backend APIs respond at `/move-api/health`
- ✅ Analyze stocks, view portfolio, get explanations

---

## Architecture

```
┌─────────────────────────────────┐
│   Hugging Face Spaces           │
│   Docker Container (Port 7860)  │
├─────────────────────────────────┤
│                                 │
│  ┌──────────────────────────┐   │
│  │   Nginx (Port 7860)      │   │
│  │   Reverse Proxy          │   │
│  └──────────────────────────┘   │
│         ↙              ↖         │
│    ┌─────────┐    ┌──────────┐  │
│    │ Frontend │    │  Backend │  │
│    │ Next.js  │    │ FastAPI  │  │
│    │ Static   │    │ Port 8000│  │
│    └─────────┘    └──────────┘  │
│                        ↓         │
│                  ┌─────────────┐ │
│                  │ Agents      │ │
│                  │ Market Data │ │
│                  │ Causal Inf  │ │
│                  └─────────────┘ │
└─────────────────────────────────┘
```

---

## Troubleshooting

### Build Fails

Check logs for errors:
1. Go to your Space → **"Logs"** tab
2. Common issues:
   - Missing `requirements.txt` entries → Add to [move_backend/requirements.txt](move_backend/requirements.txt)
   - Node.js build fails → Check [move_frontend/package.json](move_frontend/package.json)
   - Nginx config error → Check [nginx.conf](nginx.conf)

### App Shows "Bad Gateway" (502)

Usually means backend isn't responding:
- Wait 30 seconds (backend takes time to start)
- Check logs: Are both services starting?
- Verify ports: Backend=8000, Nginx=7860

### WebSocket Not Connecting

The app shows "Connecting..." but never connects:
1. Check browser console for errors (F12 → Console)
2. Verify Nginx proxy is passing WebSocket headers (it does by default)
3. Check if backend `/ws/updates` endpoint is running

### Real-time Updates Not Working

If live feed doesn't update:
1. Check backend is running: `/health` endpoint
2. Verify market data is fetching: Check logs
3. May need adjustment to price thresholds (see [move_backend/services/price_watcher.py](move_backend/services/price_watcher.py))

---

## Local Testing (Optional)

Before deploying to HF Spaces, test locally with Docker:

```bash
# Build image
docker build -t move-app .

# Run container
docker run -p 7860:7860 move-app

# Access at http://localhost:7860
```

---

## Updating Your Deployment

To push new changes:

```bash
git add .
git commit -m "Your changes"
git push huggingface main
```

HF Spaces will automatically rebuild and redeploy within minutes.

---

## Environment Variables

To add environment variables in HF Spaces:

1. Go to your Space settings
2. Under **"Repository secrets"**, add:
   - `YOUR_VAR_NAME` = value

Available env vars for Move:
- `NEXT_PUBLIC_BACKEND_WS_URL` - Override WebSocket URL (optional)
- `NEXT_PUBLIC_API_BASE_URL` - Override API base (defaults to `/move-api`)

---

## Limitations & Considerations

| Aspect | Details |
|--------|---------|
| **Storage** | Ephemeral (data lost on restart) |
| **Memory** | ~4GB (may limit large analyses) |
| **CPU** | Free tier is CPU-only (no GPU) |
| **Uptime** | May sleep after 48h inactivity (free tier) |
| **Cold Starts** | Backend takes ~3s to initialize |
| **Market Data** | Uses yfinance (real-time) |

---

## Next Steps

✅ **Deployed successfully?** Great! You can:

1. **Share your Space** - Use the "Share" button to invite others
2. **Add custom domain** - Link your own domain (paid feature)
3. **Scale up** - Upgrade to GPU hardware if needed (paid)
4. **Customize** - Modify agents/strategies and redeploy

---

## Questions?

- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- Docker Docs: https://docs.docker.com/
- Your Move repo: https://github.com/YOUR_USERNAME/Move

---

**Deployment Date:** April 2026
**Move Version:** v4
