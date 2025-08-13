#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting CityCamp AI setup on $(date)"

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI v2 (if not already installed)
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
    rm -rf awscliv2.zip aws/
fi

# Install git and other utilities
yum install -y git htop

# Create application directory
mkdir -p /opt/citycamp-ai
cd /opt/citycamp-ai

# Create data directory for persistence
mkdir -p /data
chmod 755 /data

# Mount the additional EBS volume for data persistence
if [ -e /dev/nvme1n1 ]; then
    # Check if filesystem exists
    if ! blkid /dev/nvme1n1; then
        mkfs.ext4 /dev/nvme1n1
    fi
    mount /dev/nvme1n1 /data
    echo '/dev/nvme1n1 /data ext4 defaults,nofail 0 2' >> /etc/fstab
fi

# Create directories for persistent data
mkdir -p /data/postgres /data/redis /data/app-data
chown -R 999:999 /data/postgres  # postgres user
chown -R 999:999 /data/redis     # redis user

# Get environment variables from SSM Parameter Store
echo "Fetching environment variables from SSM..."

# Function to get SSM parameter
get_ssm_param() {
    aws ssm get-parameter --region us-east-2 --name "$1" --with-decryption --query 'Parameter.Value' --output text 2>/dev/null || echo ""
}

# Get all parameters and create secure secret files
echo "Creating secure secret files for Docker..."
mkdir -p /opt/citycamp-ai/secrets
chmod 700 /opt/citycamp-ai/secrets

DATABASE_PASSWORD=$(get_ssm_param "/citycamp-ai/database-password")
SECRET_KEY=$(get_ssm_param "/citycamp-ai/secret-key")
OPENAI_API_KEY=$(get_ssm_param "/citycamp-ai/openai-api-key")
SMTP_USERNAME=$(get_ssm_param "/citycamp-ai/smtp-username")
SMTP_PASSWORD=$(get_ssm_param "/citycamp-ai/smtp-password")
TWILIO_ACCOUNT_SID=$(get_ssm_param "/citycamp-ai/twilio-account-sid")
TWILIO_AUTH_TOKEN=$(get_ssm_param "/citycamp-ai/twilio-auth-token")
TWILIO_PHONE_NUMBER=$(get_ssm_param "/citycamp-ai/twilio-phone-number")
GEOCODIO_API_KEY=$(get_ssm_param "/citycamp-ai/GEOCODIO_API_KEY")

# Create secret files with proper permissions
echo "$DATABASE_PASSWORD" > /opt/citycamp-ai/secrets/db_password
echo "$SECRET_KEY" > /opt/citycamp-ai/secrets/secret_key
echo "$OPENAI_API_KEY" > /opt/citycamp-ai/secrets/openai_api_key
echo "$SMTP_PASSWORD" > /opt/citycamp-ai/secrets/smtp_password
echo "$TWILIO_AUTH_TOKEN" > /opt/citycamp-ai/secrets/twilio_auth_token
echo "$GEOCODIO_API_KEY" > /opt/citycamp-ai/secrets/geocodio_api_key

# Secure the secret files
chmod 600 /opt/citycamp-ai/secrets/*
chown root:root /opt/citycamp-ai/secrets/*

echo "✅ Docker secrets created securely"

# Create docker-compose.yml with Docker secrets for sensitive data
cat > docker-compose.yml << 'EOF'
version: '3.8'

secrets:
  db_password:
    file: /opt/citycamp-ai/secrets/db_password
  secret_key:
    file: /opt/citycamp-ai/secrets/secret_key
  openai_api_key:
    file: /opt/citycamp-ai/secrets/openai_api_key
  smtp_password:
    file: /opt/citycamp-ai/secrets/smtp_password
  twilio_auth_token:
    file: /opt/citycamp-ai/secrets/twilio_auth_token
  geocodio_api_key:
    file: /opt/citycamp-ai/secrets/geocodio_api_key

services:
  postgres:
    image: postgres:15
    container_name: citycamp-postgres
    environment:
      POSTGRES_DB: citycamp_db
      POSTGRES_USER: citycamp_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
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
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    image: python:3.11-slim
    container_name: citycamp-backend
    working_dir: /app
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL_TEMPLATE=postgresql://citycamp_user:DB_PASSWORD_PLACEHOLDER@postgres:5432/citycamp_db
      - REDIS_URL=redis://redis:6379/0
      - SMTP_USERNAME=$SMTP_USERNAME
      - TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
      - TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
    secrets:
      - db_password
      - secret_key
      - openai_api_key
      - smtp_password
      - twilio_auth_token
      - geocodio_api_key
    ports:
      - "8000:8000"
    volumes:
      - /opt/citycamp-ai/backend:/app
      - /data/app-data:/app/data
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: >
      bash -c "
        echo 'Setting up secure environment from Docker secrets...' &&
        export DATABASE_PASSWORD=\$$(cat /run/secrets/db_password) &&
        export SECRET_KEY=\$$(cat /run/secrets/secret_key) &&
        export OPENAI_API_KEY=\$$(cat /run/secrets/openai_api_key) &&
        export SMTP_PASSWORD=\$$(cat /run/secrets/smtp_password) &&
        export TWILIO_AUTH_TOKEN=\$$(cat /run/secrets/twilio_auth_token) &&
        export GEOCODIO_API_KEY=\$$(cat /run/secrets/geocodio_api_key) &&
        export DATABASE_URL=\$${DATABASE_URL_TEMPLATE/DB_PASSWORD_PLACEHOLDER/\$$DATABASE_PASSWORD} &&
        echo 'Installing dependencies...' &&
        pip install -r requirements.txt &&
        echo 'Running database migrations...' &&
        python -m alembic upgrade head &&
        echo 'Starting CityCamp AI Backend...' &&
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
      "

  nginx:
    image: nginx:alpine
    container_name: citycamp-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /opt/citycamp-ai/nginx.conf:/etc/nginx/nginx.conf
      - /opt/citycamp-ai/frontend/dist:/usr/share/nginx/html
    depends_on:
      - backend
    restart: unless-stopped

EOF

# Create nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name _;

        # Health check endpoint
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # API endpoints
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;

            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
    }
}
EOF

# Create environment file for non-sensitive configuration only
cat > .env << EOF
SMTP_USERNAME=$SMTP_USERNAME
TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
# Sensitive data now managed via Docker secrets
EOF

# Clone the application code (parameterized repo URL, supports authenticated cloning)
echo "Cloning application code..."

# Get repository URL from SSM Parameter Store or environment variable
REPO_URL=$(get_ssm_param "/citycamp-ai/repository-url")
REPO_URL="${REPO_URL:-$REPOSITORY_URL}"

# Set default repository URL if not provided (fallback)
if [ -z "$REPO_URL" ]; then
    echo "WARNING: REPO_URL not set in SSM or environment. Using default public repository."
    REPO_URL="https://github.com/kaizengrowth/CityCamp_AI.git"
fi

echo "Repository URL: $REPO_URL"

# Get optional Git token for authenticated cloning
GIT_TOKEN=$(get_ssm_param "/citycamp-ai/git-token")
GIT_TOKEN="${GIT_TOKEN:-$GIT_TOKEN}"

if [ -n "$GIT_TOKEN" ]; then
    echo "Using authenticated clone with token"
    # Authenticated HTTPS clone (inject token into URL)
    AUTH_REPO_URL=$(echo "$REPO_URL" | sed -E "s#https://#https://$GIT_TOKEN@#")
    git clone "$AUTH_REPO_URL" temp_repo || {
        echo "ERROR: Authenticated clone failed. Aborting deployment."
        exit 1
    }
else
    echo "Using public clone (no authentication token)"
    git clone "$REPO_URL" temp_repo || {
        echo "ERROR: Repository clone failed. Aborting deployment."
        exit 1
    }
fi

if [ -d "temp_repo/backend" ]; then
    cp -r temp_repo/backend ./
    cp -r temp_repo/frontend ./
    rm -rf temp_repo
    echo "✅ Application code cloned successfully"
else
    echo "❌ ERROR: Repository structure invalid - missing backend directory"
    exit 1
fi

# Install Node.js for frontend building
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
yum install -y nodejs

# Build frontend if it exists
if [ -d "frontend" ]; then
    cd frontend
    # Install frontend dependencies and build
    npm ci
    npm run build
    cd ..
fi

# Start the application
echo "Starting CityCamp AI application..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check if services are running
docker-compose ps

echo "CityCamp AI setup completed on $(date)"
echo "Application should be accessible at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
