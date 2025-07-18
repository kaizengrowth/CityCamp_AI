#!/bin/bash

# CityCamp AI Development Start Script
echo "🚀 Starting CityCamp AI Development Environment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

print_step "1. Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

print_step "2. Waiting for database to be ready..."
sleep 3

print_step "3. Starting backend server..."
echo "   Backend will be available at: http://localhost:8002"
echo "   API documentation: http://localhost:8002/docs"
echo "   Health check: http://localhost:8002/health"
echo ""
echo "🎯 Press Ctrl+C to stop the server"
echo ""

# Start the backend server
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
