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

# Get all parameters
DATABASE_PASSWORD=$(get_ssm_param "/citycamp-ai/database-password")
SECRET_KEY=$(get_ssm_param "/citycamp-ai/secret-key")
OPENAI_API_KEY=$(get_ssm_param "/citycamp-ai/openai-api-key")
SMTP_USERNAME=$(get_ssm_param "/citycamp-ai/smtp-username")
SMTP_PASSWORD=$(get_ssm_param "/citycamp-ai/smtp-password")
TWILIO_ACCOUNT_SID=$(get_ssm_param "/citycamp-ai/twilio-account-sid")
TWILIO_AUTH_TOKEN=$(get_ssm_param "/citycamp-ai/twilio-auth-token")
TWILIO_PHONE_NUMBER=$(get_ssm_param "/citycamp-ai/twilio-phone-number")
GEOCODIO_API_KEY=$(get_ssm_param "/citycamp-ai/GEOCODIO_API_KEY")

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
      POSTGRES_PASSWORD: $DATABASE_PASSWORD
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
      - DATABASE_URL=postgresql://citycamp_user:$DATABASE_PASSWORD@postgres:5432/citycamp_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=$SECRET_KEY
      - OPENAI_API_KEY=$OPENAI_API_KEY
      - SMTP_USERNAME=$SMTP_USERNAME
      - SMTP_PASSWORD=$SMTP_PASSWORD
      - TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
      - TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
      - GEOCODIO_API_KEY=$GEOCODIO_API_KEY
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
        pip install -r requirements.txt &&
        python -m alembic upgrade head &&
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

# Create environment file
cat > .env << EOF
DATABASE_PASSWORD=$DATABASE_PASSWORD
SECRET_KEY=$SECRET_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
SMTP_USERNAME=$SMTP_USERNAME
SMTP_PASSWORD=$SMTP_PASSWORD
TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
GEOCODIO_API_KEY=$GEOCODIO_API_KEY
EOF

# Clone the application code (you'll need to update this with your repo)
echo "Cloning application code..."
git clone https://github.com/kaizengrowth/CityCamp_AI.git temp_repo || true
if [ -d "temp_repo/backend" ]; then
    cp -r temp_repo/backend ./
    cp -r temp_repo/frontend ./
    rm -rf temp_repo
fi

# Build frontend if it exists
if [ -d "frontend" ]; then
    cd frontend
    # You might need to install Node.js and build the frontend
    # For now, we'll assume the dist folder is already built
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
