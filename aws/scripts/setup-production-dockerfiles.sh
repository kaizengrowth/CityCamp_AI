#!/bin/bash

# Setup Production Dockerfiles
# This script updates the Dockerfiles for production deployment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Update backend Dockerfile for production
update_backend_dockerfile() {
    print_status "Updating backend Dockerfile for production..."

    cat > backend/Dockerfile.prod << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application (production mode)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    print_status "Backend production Dockerfile created!"
}

# Update frontend Dockerfile for production
update_frontend_dockerfile() {
    print_status "Updating frontend Dockerfile for production..."

    cat > frontend/Dockerfile.prod << 'EOF'
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF

    # Create nginx configuration for SPA
    cat > frontend/nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Handle static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

    print_status "Frontend production Dockerfile and nginx config created!"
}

# Create production docker-compose file
create_production_compose() {
    print_status "Creating production docker-compose file..."

    cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: citycamp_backend_prod
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: citycamp_frontend_prod
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

    print_status "Production docker-compose file created!"
}

# Create production environment file template
create_production_env_template() {
    print_status "Creating production environment file template..."

    cat > .env.production.template << 'EOF'
# Production Environment Variables for CityCamp AI

# Database Configuration
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/citycamp_db
DATABASE_HOST=your-rds-endpoint
DATABASE_PORT=5432
DATABASE_NAME=citycamp_db
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_secure_password

# Redis Configuration
REDIS_URL=redis://your-elasticache-endpoint:6379/0

# Security
SECRET_KEY=your-super-secure-secret-key-here
ENVIRONMENT=production
DEBUG=False

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket-name

# External APIs
OPENAI_API_KEY=your-openai-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS Configuration
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# City Data Sources
TULSA_CITY_COUNCIL_API_URL=https://api.tulsa.gov
TULSA_CITY_COUNCIL_API_KEY=your-api-key
EOF

    print_status "Production environment template created!"
}

# Create production build script
create_production_build_script() {
    print_status "Creating production build script..."

    cat > scripts/build-production.sh << 'EOF'
#!/bin/bash

# Production Build Script for CityCamp AI

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.production exists
if [ ! -f .env.production ]; then
    print_error ".env.production file not found!"
    print_warning "Please copy .env.production.template to .env.production and fill in your values."
    exit 1
fi

# Build backend production image
print_status "Building backend production image..."
docker build -f backend/Dockerfile.prod -t citycamp-ai-backend:prod ./backend

# Build frontend production image
print_status "Building frontend production image..."
docker build -f frontend/Dockerfile.prod -t citycamp-ai-frontend:prod ./frontend

print_status "Production images built successfully!"
print_status "You can now run: docker-compose -f docker-compose.prod.yml up -d"
EOF

    chmod +x scripts/build-production.sh
    print_status "Production build script created!"
}

# Main function
main() {
    print_status "Setting up production Dockerfiles and configuration..."

    update_backend_dockerfile
    update_frontend_dockerfile
    create_production_compose
    create_production_env_template
    create_production_build_script

    print_status "Production setup completed!"
    print_warning "Next steps:"
    print_warning "1. Copy .env.production.template to .env.production"
    print_warning "2. Fill in your production environment variables"
    print_warning "3. Run: ./scripts/build-production.sh"
    print_warning "4. Run: docker-compose -f docker-compose.prod.yml up -d"
}

# Run main function
main "$@"
