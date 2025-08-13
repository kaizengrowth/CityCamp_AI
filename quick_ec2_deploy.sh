#!/bin/bash

# Quick EC2 Deployment Script for CityCamp AI (Non-interactive)
# Run this script on your EC2 instance after setting environment variables

set -e

echo "🚀 Quick deployment of CityCamp AI..."
echo "====================================="

# Check if required environment variables are set
if [[ -z "$DATABASE_URL" || -z "$SECRET_KEY" || -z "$OPENAI_API_KEY" || -z "$GEOCODIO_API_KEY" ]]; then
    echo "❌ Error: Required environment variables not set!"
    echo "Please set these environment variables before running:"
    echo "export DATABASE_URL='postgresql://...'"
    echo "export SECRET_KEY='your-secret-key'"
    echo "export OPENAI_API_KEY='your-openai-key'"
    echo "export GEOCODIO_API_KEY='your-geocodio-key'"
    exit 1
fi

# Navigate to home directory
cd /home/ec2-user

# Clone or update repository
echo "📥 Setting up repository..."
if [ -d "citycamp-ai" ]; then
    cd citycamp-ai
    git fetch origin
    git reset --hard origin/main
    git checkout main
    git pull origin main
else
    git clone https://github.com/kaizengrowth/CityCamp_AI.git citycamp-ai
    cd citycamp-ai
    git checkout main
fi

echo "Current commit: $(git rev-parse --short HEAD)"

# Set up secrets
echo "🔐 Setting up secrets..."
mkdir -p secrets

echo "$DATABASE_URL" > secrets/database_url
echo "$SECRET_KEY" > secrets/secret_key
echo "$OPENAI_API_KEY" > secrets/openai_api_key
echo "$GEOCODIO_API_KEY" > secrets/geocodio_api_key

chmod 600 secrets/*
chmod 700 secrets

# Stop and remove existing containers
echo "🛑 Cleaning up existing containers..."
docker stop citycamp-backend citycamp-frontend 2>/dev/null || true
docker rm citycamp-backend citycamp-frontend 2>/dev/null || true
docker image prune -f || true

# Build and start backend
echo "🔨 Building and starting backend..."
docker build -t citycamp-ai-backend ./backend/

docker run -d --name citycamp-backend \
    -p 8000:8000 \
    -p 80:8000 \
    -v $(pwd)/secrets:/app/secrets:ro \
    --restart unless-stopped \
    citycamp-ai-backend

# Health check
echo "🔍 Waiting for service to start..."
sleep 30

if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "🌐 Service is running on:"
    echo "   - http://localhost:8000/health"
    echo "   - https://tulsai.city (Load Balancer)"
else
    echo "❌ Health check failed!"
    echo "Container logs:"
    docker logs citycamp-backend
    exit 1
fi
