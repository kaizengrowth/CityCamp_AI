#!/bin/bash

# Initialize Notification Topics in Production
# Usage: ./scripts/init_production_topics.sh [PRODUCTION_URL]

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

# Get production URL
PRODUCTION_URL=${1:-}

if [ -z "$PRODUCTION_URL" ]; then
    print_error "Please provide your production URL"
    echo "Usage: $0 https://your-domain.com"
    echo "   or: $0 http://your-alb-dns-name.elb.amazonaws.com"
    exit 1
fi

# Remove trailing slash
PRODUCTION_URL=${PRODUCTION_URL%/}

print_status "Initializing notification topics in production..."
print_status "Target: $PRODUCTION_URL"

# Initialize topics
ENDPOINT="$PRODUCTION_URL/api/v1/subscriptions/admin/initialize-topics"

print_status "Calling: $ENDPOINT"

if response=$(curl -s -w "%{http_code}" -X POST "$ENDPOINT"); then
    http_code="${response: -3}"
    body="${response%???}"

    if [ "$http_code" = "200" ]; then
        print_status "✅ Topics initialized successfully!"
        echo "$body" | grep -q "topics_created" && echo "Response: $body"
    else
        print_error "❌ Failed with HTTP $http_code"
        echo "Response: $body"
        exit 1
    fi
else
    print_error "❌ Failed to connect to $ENDPOINT"
    print_warning "Make sure your production server is running and accessible"
    exit 1
fi

print_status "🎉 Production notification system is ready!"
echo ""
echo "You can now test the signup form at:"
echo "$PRODUCTION_URL/signup/notifications"
