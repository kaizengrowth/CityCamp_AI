#!/bin/bash
# Development Environment Activation Script
# Usage: source scripts/activate-dev.sh

echo "🔧 Setting up CityCamp AI development environment..."

# Navigate to project root if not already there
if [[ ! -f "backend/venv/bin/activate" ]]; then
    echo "❌ Error: Run this script from the project root directory"
    return 1 2>/dev/null || exit 1
fi

# Activate virtual environment
source backend/venv/bin/activate
echo "🐍 Virtual environment activated: $(which python)"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
echo "📦 PYTHONPATH configured"

# Set environment variables
export NODE_ENV=development
export DATABASE_URL="postgresql://citycamp_user:CityCamp2005%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/postgres"

echo ""
echo "✅ Development environment ready!"
echo ""
echo "🚀 To start development servers:"
echo "   Backend:  cd backend && python -m app.main"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "🔗 URLs:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3003"
echo "   API Docs: http://localhost:8000/docs"
