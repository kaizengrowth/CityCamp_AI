#!/bin/bash

# CityCamp AI Backend Setup Script
echo "🚀 Setting up CityCamp AI Backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1-2)
if [ -z "$python_version" ]; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

print_status "Python version: $python_version"

# Navigate to backend directory
cd backend || { print_error "Backend directory not found!"; exit 1; }

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    print_warning "Please update the .env file with your API keys and database credentials."
fi

# Create alembic migration directory
print_status "Initializing database migrations..."
alembic init -t async alembic

print_status "✅ Backend setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "cd backend && source venv/bin/activate"
echo ""
echo "To start the development server, run:"
echo "uvicorn app.main:app --reload"
echo ""
echo "Don't forget to:"
echo "1. Update your .env file with API keys"
echo "2. Set up your PostgreSQL database"
echo "3. Run database migrations: alembic upgrade head"
