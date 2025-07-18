#!/bin/bash

# CityCamp AI Dependency Fix Script
echo "🔧 Fixing dependency conflicts for CityCamp AI..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_step "1. Creating a fresh virtual environment..."
cd backend

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    print_warning "Removing existing virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
print_status "Creating new virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

print_step "2. Installing clean dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_step "3. Creating .env file if needed..."
if [ ! -f ".env" ]; then
    cp env.example .env
    print_warning "Please update the .env file with your API keys"
fi

print_status "✅ Dependencies resolved successfully!"
echo ""
echo "Virtual environment is now active. To reactivate it later:"
echo "cd backend && source venv/bin/activate"
echo ""
echo "To start the development server:"
echo "uvicorn app.main:app --reload"
