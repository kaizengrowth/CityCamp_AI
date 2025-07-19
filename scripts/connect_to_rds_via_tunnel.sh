#!/bin/bash

# Connect to RDS via ECS Task Tunnel
# This script creates a secure tunnel to RDS through an ECS task

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
CLUSTER_NAME="citycamp-ai-cluster"
SERVICE_NAME="citycamp-ai-service"
LOCAL_PORT="5433"
RDS_HOST="citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com"
RDS_PORT="5432"

print_status "Setting up RDS tunnel via ECS task..."

# Get running ECS task
print_status "Finding running ECS task..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --desired-status RUNNING --query 'taskArns[0]' --output text)

if [ "$TASK_ARN" = "None" ] || [ -z "$TASK_ARN" ]; then
    print_error "No running ECS tasks found. Please ensure your application is running on ECS."
    exit 1
fi

TASK_ID=$(basename $TASK_ARN)
print_success "Found running task: $TASK_ID"

# Start Session Manager session with port forwarding
print_status "Starting port forwarding session..."
print_status "Local port $LOCAL_PORT will forward to RDS ($RDS_HOST:$RDS_PORT)"
print_warning "Keep this terminal open while using the database connection"

# Create the tunnel
aws ecs execute-command \
    --cluster $CLUSTER_NAME \
    --task $TASK_ARN \
    --container citycamp-ai-backend \
    --interactive \
    --command "/bin/bash -c 'echo \"Setting up port forward to RDS...\"; socat TCP-LISTEN:8080,reuseaddr,fork TCP:$RDS_HOST:$RDS_PORT'"

print_success "Tunnel established!"
print_status "You can now connect to PostgreSQL using:"
print_status "Host: localhost"
print_status "Port: $LOCAL_PORT"
print_status "Database: citycamp_db"
print_status "Username: citycamp_user"
print_status "Password: CityCampSecure2024!"

print_warning "Press Ctrl+C to close the tunnel when done"
