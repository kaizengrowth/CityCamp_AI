#!/bin/bash

# Script to create SSM parameters for CityCamp AI deployment
# Run this script before deploying to ECS

set -e

AWS_REGION="us-east-1"
PARAMETER_PREFIX="/citycamp-ai"

echo "🔧 Setting up SSM parameters for CityCamp AI..."

# Function to create a parameter
create_parameter() {
    local name="$1"
    local value="$2"
    local type="$3"
    local description="$4"

    echo "Creating parameter: $name"
    aws ssm put-parameter \
        --name "$name" \
        --value "$value" \
        --type "$type" \
        --description "$description" \
        --region "$AWS_REGION" \
        --overwrite \
        --no-cli-pager
}

# Database URL - construct from Terraform outputs
echo "📊 Getting database information from Terraform..."
cd "$(dirname "$0")/../terraform"

# Get RDS endpoint from Terraform state
DB_ENDPOINT=$(terraform output -raw rds_endpoint 2>/dev/null || echo "your-rds-endpoint.region.rds.amazonaws.com")
DB_NAME=$(terraform output -raw db_name 2>/dev/null || echo "citycamp_db")
DB_USERNAME=$(terraform output -raw db_username 2>/dev/null || echo "postgres")
DB_PASSWORD="REDACTED_PASSWORD"  # From terraform.tfvars

# Get Redis endpoint from Terraform state
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint 2>/dev/null || echo "your-redis-cluster.cache.amazonaws.com")

# Construct connection strings
DATABASE_URL="postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/${DB_NAME}"
REDIS_URL="redis://${REDIS_ENDPOINT}:6379/0"

echo "🔐 Creating SSM parameters..."

# Required parameters
create_parameter "${PARAMETER_PREFIX}/database-url" "$DATABASE_URL" "SecureString" "PostgreSQL database connection URL"
create_parameter "${PARAMETER_PREFIX}/redis-url" "$REDIS_URL" "SecureString" "Redis connection URL"
create_parameter "${PARAMETER_PREFIX}/secret-key" "$(openssl rand -base64 32)" "SecureString" "Django secret key for session encryption"

# OpenAI API Key (you'll need to set this manually)
echo "⚠️  Please set your OpenAI API key:"
read -s -p "Enter OpenAI API Key: " OPENAI_KEY
echo
create_parameter "${PARAMETER_PREFIX}/openai-api-key" "$OPENAI_KEY" "SecureString" "OpenAI API key for chatbot functionality"

# Google API Key for web search (optional)
echo "🔍 Google Custom Search API (optional - press Enter to skip):"
read -s -p "Enter Google API Key (optional): " GOOGLE_KEY
if [ -n "$GOOGLE_KEY" ]; then
    create_parameter "${PARAMETER_PREFIX}/google-api-key" "$GOOGLE_KEY" "SecureString" "Google Custom Search API key"

    read -p "Enter Google Search Engine ID: " GOOGLE_SEARCH_ID
    create_parameter "${PARAMETER_PREFIX}/google-search-engine-id" "$GOOGLE_SEARCH_ID" "String" "Google Custom Search Engine ID"
fi

# Twilio settings (optional - you can set placeholder values)
echo "📱 Twilio settings (optional - press Enter to use placeholders):"
read -p "Enter Twilio Account SID (or press Enter for placeholder): " TWILIO_SID
TWILIO_SID=${TWILIO_SID:-"placeholder_twilio_sid"}

read -s -p "Enter Twilio Auth Token (or press Enter for placeholder): " TWILIO_TOKEN
echo
TWILIO_TOKEN=${TWILIO_TOKEN:-"placeholder_twilio_token"}

read -p "Enter Twilio Phone Number (or press Enter for placeholder): " TWILIO_PHONE
TWILIO_PHONE=${TWILIO_PHONE:-"+1234567890"}

create_parameter "${PARAMETER_PREFIX}/twilio-account-sid" "$TWILIO_SID" "SecureString" "Twilio Account SID for SMS notifications"
create_parameter "${PARAMETER_PREFIX}/twilio-auth-token" "$TWILIO_TOKEN" "SecureString" "Twilio Auth Token"
create_parameter "${PARAMETER_PREFIX}/twilio-phone-number" "$TWILIO_PHONE" "String" "Twilio phone number for SMS"

# SMTP settings (optional - you can set placeholder values)
echo "📧 SMTP settings (optional - press Enter to use placeholders):"
read -p "Enter SMTP Username (or press Enter for placeholder): " SMTP_USER
SMTP_USER=${SMTP_USER:-"placeholder_smtp_user"}

read -s -p "Enter SMTP Password (or press Enter for placeholder): " SMTP_PASS
echo
SMTP_PASS=${SMTP_PASS:-"placeholder_smtp_password"}

create_parameter "${PARAMETER_PREFIX}/smtp-username" "$SMTP_USER" "SecureString" "SMTP username for email notifications"
create_parameter "${PARAMETER_PREFIX}/smtp-password" "$SMTP_PASS" "SecureString" "SMTP password for email notifications"

echo "✅ All SSM parameters have been created successfully!"
echo ""
echo "📋 Summary of created parameters:"
echo "  - ${PARAMETER_PREFIX}/database-url"
echo "  - ${PARAMETER_PREFIX}/redis-url"
echo "  - ${PARAMETER_PREFIX}/secret-key"
echo "  - ${PARAMETER_PREFIX}/openai-api-key"
echo "  - ${PARAMETER_PREFIX}/twilio-account-sid"
echo "  - ${PARAMETER_PREFIX}/twilio-auth-token"
echo "  - ${PARAMETER_PREFIX}/twilio-phone-number"
echo "  - ${PARAMETER_PREFIX}/smtp-username"
echo "  - ${PARAMETER_PREFIX}/smtp-password"

if [ -n "$GOOGLE_KEY" ]; then
    echo "  - ${PARAMETER_PREFIX}/google-api-key"
    echo "  - ${PARAMETER_PREFIX}/google-search-engine-id"
fi

echo ""
echo "🚀 You can now deploy your ECS service!"
echo "   Run: aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment"
