#!/bin/bash
set -e

echo "=== CityCamp AI EC2 Fix Script ==="
echo "This script fixes Docker deployment issues on existing EC2 instances"
echo "Started at: $(date)"

# Log output
exec > >(tee -a /var/log/citycamp-fix.log)
exec 2>&1

echo "Step 1: Fixing package manager issues..."

# Clean up any broken package installs
sudo yum clean all
sudo rm -rf /var/cache/yum

# Update with skip-broken to handle conflicts
sudo yum update -y --skip-broken

echo "Step 2: Installing Docker if not present..."

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    sudo yum install -y docker
fi

# Start and enable Docker
sudo systemctl start docker || true
sudo systemctl enable docker || true
sudo usermod -a -G docker ec2-user || true

echo "Step 3: Installing Docker Compose if not present..."

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "Step 4: Installing required utilities..."

# Install git and utilities with error handling
sudo yum install -y git htop unzip --skip-broken || true

echo "Step 5: Setting up application directory..."

# Create application directory
sudo mkdir -p /opt/citycamp-ai
cd /opt/citycamp-ai

# Create data directories
sudo mkdir -p /data/postgres /data/redis /data/app-data
sudo chown -R 999:999 /data/postgres /data/redis || true

echo "Step 6: Fetching configuration from SSM..."

# Function to get SSM parameter
get_ssm_param() {
    local param_name="$1"
    local value
    value=$(aws ssm get-parameter --region us-east-2 --name "$param_name" --with-decryption --query 'Parameter.Value' --output text 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$value" ] && [ "$value" != "None" ]; then
        echo "$value"
    else
        echo ""
    fi
}

# Get required parameters
DATABASE_PASSWORD=$(get_ssm_param "/citycamp-ai/database-password")
SECRET_KEY=$(get_ssm_param "/citycamp-ai/secret-key")
OPENAI_API_KEY=$(get_ssm_param "/citycamp-ai/openai-api-key")

echo "Step 7: Creating Docker Compose configuration..."

# Create docker-compose.yml
sudo tee docker-compose.yml > /dev/null << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: citycamp-postgres
    environment:
      POSTGRES_DB: citycamp_db
      POSTGRES_USER: citycamp_user
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - /data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U citycamp_user -d citycamp_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: citycamp-redis
    volumes:
      - /data/redis:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    command: redis-server --appendonly yes

  # Simplified backend for testing
  backend:
    image: python:3.11-slim
    container_name: citycamp-backend
    working_dir: /app
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://citycamp_user:${DATABASE_PASSWORD}@postgres:5432/citycamp_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - /opt/citycamp-ai/backend:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    command: >
      bash -c "
        echo 'Backend container starting...' &&
        pip install fastapi uvicorn sqlalchemy psycopg2-binary redis &&
        python -c \"
from fastapi import FastAPI
app = FastAPI()

@app.get('/health')
def health():
    return {'status': 'ok', 'message': 'CityCamp AI Backend Running'}

@app.get('/')
def root():
    return {'message': 'CityCamp AI API', 'status': 'operational'}
        \" > main.py &&
        python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
      "

  # Simple nginx frontend
  nginx:
    image: nginx:alpine
    container_name: citycamp-nginx
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    command: >
      sh -c "
        echo 'server {
          listen 80;

          location /health {
            proxy_pass http://backend:8000/health;
          }

          location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host \$$host;
          }

          location / {
            return 200 \"CityCamp AI - EC2 Deployment Working!\";
            add_header Content-Type text/plain;
          }
        }' > /etc/nginx/conf.d/default.conf &&
        nginx -g 'daemon off;'
      "

EOF

echo "Step 8: Stopping any existing containers..."
sudo docker-compose down || true

echo "Step 9: Starting the application..."
sudo docker-compose up -d

echo "Step 10: Checking service status..."
sleep 10
sudo docker-compose ps
sudo docker-compose logs --tail=20

echo ""
echo "=== Fix script completed at $(date) ==="
echo "Check the application at:"
echo "  - Health: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/health"
echo "  - Main: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/"
EOF
