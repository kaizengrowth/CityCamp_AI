#!/bin/bash

# Manual EC2 Deployment Script for CityCamp AI
# Run this script on your EC2 instance (3.138.240.133) as ec2-user

set -e

echo "🚀 Starting manual deployment of CityCamp AI..."
echo "================================================"

# Navigate to home directory
cd /home/ec2-user

# Step 1: Clone or update repository
echo "📥 Setting up repository..."
if [ -d "citycamp-ai" ]; then
    echo "Updating existing repository..."
    cd citycamp-ai
    git fetch origin
    git reset --hard origin/main
    git checkout main
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/kaizengrowth/CityCamp_AI.git citycamp-ai
    cd citycamp-ai
    git checkout main
fi

echo "Current commit: $(git rev-parse --short HEAD)"

# Step 2: Set up production secrets
echo "🔐 Setting up application secrets..."
mkdir -p secrets

# You need to manually set these values - replace with your actual secrets
echo "Please set up your secrets. Current values needed:"
echo "- DATABASE_URL"
echo "- SECRET_KEY"
echo "- OPENAI_API_KEY"
echo "- GEOCODIO_API_KEY"

# Example secret setup (you'll need to replace these with actual values)
read -p "Enter your DATABASE_URL: " DATABASE_URL
read -p "Enter your SECRET_KEY: " SECRET_KEY
read -p "Enter your OPENAI_API_KEY: " OPENAI_API_KEY
read -p "Enter your GEOCODIO_API_KEY: " GEOCODIO_API_KEY

# Create secret files with secure permissions
echo "$DATABASE_URL" > secrets/database_url
echo "$SECRET_KEY" > secrets/secret_key
echo "$OPENAI_API_KEY" > secrets/openai_api_key
echo "$GEOCODIO_API_KEY" > secrets/geocodio_api_key

# Set secure file permissions (owner read/write only)
chmod 600 secrets/database_url
chmod 600 secrets/secret_key
chmod 600 secrets/openai_api_key
chmod 600 secrets/geocodio_api_key

# Set directory permissions (owner read/write/execute only)
chmod 700 secrets

# Step 3: Stop existing containers
echo "🛑 Stopping existing containers..."
docker stop citycamp-backend citycamp-frontend || true
docker rm citycamp-backend citycamp-frontend || true

# Clean up any old images to free space
docker image prune -f || true

# Step 4: Build and run backend
echo "🔨 Building backend application..."
docker build -t citycamp-ai-backend ./backend/

echo "🚀 Starting backend service..."
docker run -d --name citycamp-backend \
    -p 8000:8000 \
    -p 80:8000 \
    -v $(pwd)/secrets:/app/secrets:ro \
    --restart unless-stopped \
    citycamp-ai-backend

# Step 5: Wait and run health check
echo "🔍 Running health check..."
sleep 30

# Test local health endpoint
if curl -f http://localhost:8000/health; then
    echo "✅ Backend health check passed!"
else
    echo "❌ Health check failed, checking logs..."
    docker logs citycamp-backend
    exit 1
fi

# Test external access
echo "Testing external access on port 80..."
if curl -f http://localhost:80/health; then
    echo "✅ External access on port 80 working!"
else
    echo "⚠️ Port 80 access failed, but port 8000 is working"
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Application is running at:"
echo "   - Internal: http://localhost:8000"
echo "   - External: http://3.138.240.133:8000"
echo "   - Domain: https://tulsai.city (via Load Balancer)"
echo ""
echo "🔒 Secrets are secured with 600 permissions"
echo ""
echo "To check logs: docker logs citycamp-backend"
echo "To restart: docker restart citycamp-backend"
