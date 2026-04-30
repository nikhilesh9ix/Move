# Multi-stage build for Move v4 - Production-Ready

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY move_frontend/package*.json ./
RUN npm ci
COPY move_frontend/ ./
RUN npm run build

# Stage 2: Final image with Node.js and Python
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (Node.js, Nginx, curl)
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy backend application
COPY move_backend/ ./backend/

# Copy frontend built files and source
COPY move_frontend/ ./frontend/
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Install Python dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Install frontend dependencies for production
WORKDIR /app/frontend
RUN npm ci --production

# Configure Nginx
RUN mkdir -p /var/log/nginx /var/run/nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Create startup script that runs all services
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Move v4 services..."\n\
\n\
# Start FastAPI backend on port 8000\n\
echo "Starting FastAPI backend..."\n\
cd /app/backend\n\
uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info &\n\
BACKEND_PID=$!\n\
\n\
# Wait for backend to be ready\n\
echo "Waiting for backend to start..."\n\
for i in {1..30}; do\n\
  if curl -f http://127.0.0.1:8000/health >/dev/null 2>&1; then\n\
    echo "Backend is ready!"\n\
    break\n\
  fi\n\
  if [ $i -eq 30 ]; then\n\
    echo "Backend failed to start"\n\
    exit 1\n\
  fi\n\
  sleep 1\n\
done\n\
\n\
# Start Next.js frontend on port 3000\n\
echo "Starting Next.js frontend..."\n\
cd /app/frontend\n\
npm start &\n\
FRONTEND_PID=$!\n\
\n\
# Start Nginx on port 7860\n\
echo "Starting Nginx reverse proxy on port 7860..."\n\
nginx -g "daemon off;" &\n\
NGINX_PID=$!\n\
\n\
echo "All services started successfully!"\n\
echo "App available at http://localhost:7860"\n\
\n\
# Keep script alive and forward signals\n\
wait $BACKEND_PID $FRONTEND_PID $NGINX_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

WORKDIR /app

# Expose main port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860 || exit 1

# Start all services
CMD ["/app/start.sh"]
