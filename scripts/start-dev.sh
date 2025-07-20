#!/bin/bash
# Complete Development Startup Script
# This script activates the virtual environment and starts both backend and frontend

set -e  # Exit on error

echo "🚀 Starting CityCamp AI Development Environment..."
echo "=================================================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Kill any existing processes on our ports
echo "🧹 Cleaning up existing processes..."
lsof -ti :8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :3003 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :3004 2>/dev/null | xargs kill -9 2>/dev/null || true

# Activate virtual environment
echo "🐍 Activating virtual environment..."
if [[ ! -f "backend/venv/bin/activate" ]]; then
    echo "❌ Virtual environment not found. Creating it..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    source backend/venv/bin/activate
fi

echo "✅ Virtual environment active: $(which python)"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
export NODE_ENV=development

# Create .env if it doesn't exist
if [[ ! -f "backend/.env" ]]; then
    echo "📝 Creating backend .env file..."
    ./scripts/setup_dev_environment.sh
fi

# Clear frontend caches
echo "🧹 Clearing frontend caches..."
rm -rf frontend/node_modules/.vite frontend/dist 2>/dev/null || true

echo ""
echo "🎯 Starting Services..."
echo "======================="

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend (Port 8000)..."
    cd backend
    python -m app.main > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend (Port 3003/3004)..."
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    cd ..
}

# Create logs directory
mkdir -p logs

# Start both services
start_backend
sleep 3
start_frontend

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Test services
echo ""
echo "🧪 Testing Services..."
echo "====================="

# Test backend
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: http://localhost:8000 (API Docs: http://localhost:8000/docs)"
else
    echo "❌ Backend failed to start. Check logs/backend.log"
fi

# Test frontend
if curl -s -f http://localhost:3003/ > /dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:3003"
elif curl -s -f http://localhost:3004/ > /dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:3004"
else
    echo "❌ Frontend failed to start. Check logs/frontend.log"
fi

echo ""
echo "🎉 Development environment ready!"
echo "================================="
echo ""
echo "📱 Open your browser:"
echo "   Frontend: http://localhost:3003 (or 3004)"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Monitor logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Keep script running to maintain PIDs
echo "Press Ctrl+C to stop all services..."
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for user to stop
while true; do
    sleep 1
done
