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
