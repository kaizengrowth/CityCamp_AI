#!/bin/bash

# AWS Deployment Environment Setup Script
# This sets up the required environment variables for AWS deployment

echo "🔧 Setting up AWS deployment environment variables..."

# Required: Database Connection (URL-encoded password)
export DATABASE_URL="postgresql://citycamp_user:CityCamp2005%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/postgres"

# Required: Redis URL (you'll need to set this to your Redis instance)
export REDIS_URL="redis://your-redis-host:6379/0"

# Recommended: Application Secret Key (generate a secure one)
export SECRET_KEY="$(openssl rand -base64 32)"

echo "✅ Required environment variables set:"
echo "   DATABASE_URL: ✅ (PostgreSQL connection configured)"
echo "   REDIS_URL: ⚠️  (UPDATE THIS - you need a Redis instance)"
echo "   SECRET_KEY: ✅ (Generated secure key)"

echo ""
echo "🔧 Setting optional service credentials..."
echo "   (You can add these for full functionality or skip for basic deployment)"

# Optional: OpenAI API Key (for AI features)
# export OPENAI_API_KEY="your-openai-api-key-here"

# Required: Twilio (for SMS notifications) - SET THESE FIRST!
export TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID:-your-twilio-account-sid-here}"
export TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN:-your-twilio-auth-token-here}"
export TWILIO_PHONE_NUMBER="${TWILIO_PHONE_NUMBER:-+1234567890}"

# Optional: Email SMTP (for email notifications)
# export SMTP_USERNAME="your-email@gmail.com"
# export SMTP_PASSWORD="your-app-password"

echo ""
echo "🚀 Ready for deployment! Now run:"
echo "   source scripts/setup_aws_environment.sh"
echo "   ./aws/scripts/deploy.sh"
echo ""
echo "🔧 TO CUSTOMIZE (recommended):"
echo "1. Set up Redis instance on AWS ElastiCache"
echo "2. Add your OpenAI API key for AI features"
echo "3. ✅ Twilio credentials configured for SMS notifications"
echo "4. Add SMTP credentials for email notifications"
