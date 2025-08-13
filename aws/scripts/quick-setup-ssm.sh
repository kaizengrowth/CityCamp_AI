#!/bin/bash

# Quick setup script for essential SSM parameters
# Uses actual infrastructure endpoints from Terraform

set -e

AWS_REGION="us-east-1"
PARAMETER_PREFIX="/citycamp-ai"

echo "🚀 Quick setup of essential SSM parameters for CityCamp AI..."

# Check for required environment variables
if [ -z "$CITYCAMP_DB_PASSWORD" ]; then
    echo "❌ Error: CITYCAMP_DB_PASSWORD environment variable is required"
    echo "Set it with: export CITYCAMP_DB_PASSWORD='your-secure-password'"
    exit 1
fi

# Actual endpoints from Terraform output
RDS_ENDPOINT="citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com"
REDIS_ENDPOINT="citycamp-ai-redis.2gtiq7.0001.use1.cache.amazonaws.com"

# Construct connection URLs
DATABASE_URL="postgresql://postgres:${CITYCAMP_DB_PASSWORD}@${RDS_ENDPOINT}/citycamp_db"
REDIS_URL="redis://${REDIS_ENDPOINT}:6379/0"

echo "Creating essential parameters..."

# Create database URL
aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/database-url" \
    --value "$DATABASE_URL" \
    --type "SecureString" \
    --description "PostgreSQL database connection URL" \
    --region "$AWS_REGION" \
    --overwrite

# Create Redis URL
aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/redis-url" \
    --value "$REDIS_URL" \
    --type "SecureString" \
    --description "Redis connection URL" \
    --region "$AWS_REGION" \
    --overwrite

# Create secret key
SECRET_KEY=$(openssl rand -base64 32)
aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/secret-key" \
    --value "$SECRET_KEY" \
    --type "SecureString" \
    --description "Django secret key for session encryption" \
    --region "$AWS_REGION" \
    --overwrite

# Create placeholder parameters for optional services
echo "Creating parameters for optional services..."

# Prompt for OpenAI API key (required for chatbot functionality)
echo "🤖 Please enter your OpenAI API key for chatbot functionality:"
read -s -p "Enter OpenAI API Key: " OPENAI_KEY
echo

if [ -z "$OPENAI_KEY" ]; then
    echo "⚠️  No OpenAI API key provided. Using placeholder - chatbot will not work until updated."
    OPENAI_KEY="sk-placeholder-openai-key"
fi

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/openai-api-key" \
    --value "$OPENAI_KEY" \
    --type "SecureString" \
    --description "OpenAI API key for chatbot functionality" \
    --region "$AWS_REGION" \
    --overwrite

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/twilio-account-sid" \
    --value "placeholder_twilio_sid" \
    --type "SecureString" \
    --description "Twilio Account SID (placeholder)" \
    --region "$AWS_REGION" \
    --overwrite

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/twilio-auth-token" \
    --value "placeholder_twilio_token" \
    --type "SecureString" \
    --description "Twilio Auth Token (placeholder)" \
    --region "$AWS_REGION" \
    --overwrite

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/twilio-phone-number" \
    --value "+1234567890" \
    --type "String" \
    --description "Twilio phone number (placeholder)" \
    --region "$AWS_REGION" \
    --overwrite

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/smtp-username" \
    --value "placeholder_smtp_user" \
    --type "SecureString" \
    --description "SMTP username (placeholder)" \
    --region "$AWS_REGION" \
    --overwrite

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/smtp-password" \
    --value "placeholder_smtp_password" \
    --type "SecureString" \
    --description "SMTP password (placeholder)" \
    --region "$AWS_REGION" \
    --overwrite

echo "✅ Essential SSM parameters created successfully!"
echo ""
echo "📋 Created parameters:"
echo "  ✅ ${PARAMETER_PREFIX}/database-url (with real RDS endpoint)"
echo "  ✅ ${PARAMETER_PREFIX}/redis-url (with real Redis endpoint)"
echo "  ✅ ${PARAMETER_PREFIX}/secret-key (generated)"
if [ "$OPENAI_KEY" != "sk-placeholder-openai-key" ]; then
    echo "  ✅ ${PARAMETER_PREFIX}/openai-api-key (configured with your key)"
else
    echo "  ⚠️  ${PARAMETER_PREFIX}/openai-api-key (placeholder - update with real key)"
fi
echo "  📝 ${PARAMETER_PREFIX}/twilio-* (placeholders)"
echo "  📝 ${PARAMETER_PREFIX}/smtp-* (placeholders)"
echo ""
if [ "$OPENAI_KEY" != "sk-placeholder-openai-key" ]; then
    echo "🎉 Your OpenAI API key has been configured! The chatbot should work in production."
else
    echo "⚠️  IMPORTANT: Update the OpenAI API key with your real key:"
    echo "   aws ssm put-parameter --name '${PARAMETER_PREFIX}/openai-api-key' --value 'your-real-openai-key' --type 'SecureString' --overwrite --region ${AWS_REGION}"
fi
echo ""
echo "🚀 Your ECS deployment should now work!"
echo "   Run: aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment --region ${AWS_REGION}"
