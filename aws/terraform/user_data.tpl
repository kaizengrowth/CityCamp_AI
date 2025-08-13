#!/bin/bash
set -e

# Log all output
exec > >(tee -a /var/log/citycamp-setup.log)
exec 2>&1

echo "=== CityCamp AI EC2 Setup Starting ==="
echo "Started at: $(date)"

# Clean up package manager
yum clean all
rm -rf /var/cache/yum

# Update system
yum update -y --skip-broken

# Install Docker
yum install -y docker git htop unzip --skip-broken

# Start and enable Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /opt/citycamp-ai
cd /opt/citycamp-ai

# Create data directories for persistence
mkdir -p /data/postgres /data/redis /data/app-data
chown -R 999:999 /data/postgres /data/redis

# Function to get SSM parameter
get_ssm_param() {
    local param_name="$1"
    local value
    value=$(aws ssm get-parameter --region ${aws_region} --name "$param_name" --with-decryption --query 'Parameter.Value' --output text 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$value" ] && [ "$value" != "None" ]; then
        echo "$value"
    else
        echo ""
    fi
}

# Get configuration from SSM Parameter Store
DATABASE_PASSWORD=$(get_ssm_param "/citycamp-ai/database-password")
SECRET_KEY=$(get_ssm_param "/citycamp-ai/secret-key")
OPENAI_API_KEY=$(get_ssm_param "/citycamp-ai/openai-api-key")

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: citycamp-postgres
    environment:
      POSTGRES_DB: citycamp_db
      POSTGRES_USER: citycamp_user
      POSTGRES_PASSWORD: $${DATABASE_PASSWORD}
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

  # Simple backend for health checks
  backend:
    image: python:3.11-slim
    container_name: citycamp-backend
    working_dir: /app
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://citycamp_user:$${DATABASE_PASSWORD}@postgres:5432/citycamp_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=$${SECRET_KEY}
      - OPENAI_API_KEY=$${OPENAI_API_KEY}
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
    return {'status': 'ok', 'message': 'CityCamp AI Backend Running', 'region': '${aws_region}'}

@app.get('/')
def root():
    return {'message': 'CityCamp AI API', 'status': 'operational', 'region': '${aws_region}'}
        \" > main.py &&
        python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
      "

  # Nginx reverse proxy
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
            proxy_set_header Host \$$host;
            proxy_set_header X-Real-IP \$$remote_addr;
          }

          location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host \$$host;
            proxy_set_header X-Real-IP \$$remote_addr;
          }

          location / {
            return 200 \"CityCamp AI - EC2 Deployment Working in ${aws_region}!\";
            add_header Content-Type text/plain;
          }
        }' > /etc/nginx/conf.d/default.conf &&
        nginx -g 'daemon off;'
      "
EOF

# Substitute variables in docker-compose.yml
sed -i "s/\$${DATABASE_PASSWORD}/$DATABASE_PASSWORD/g" docker-compose.yml
sed -i "s/\$${SECRET_KEY}/$SECRET_KEY/g" docker-compose.yml
sed -i "s/\$${OPENAI_API_KEY}/$OPENAI_API_KEY/g" docker-compose.yml

# Start the application
docker-compose up -d

# Wait for services to be ready
sleep 15

# Check service status
docker-compose ps
docker-compose logs --tail=20

echo "=== CityCamp AI Setup Completed at $(date) ==="
echo "Application should be available on port 80"
