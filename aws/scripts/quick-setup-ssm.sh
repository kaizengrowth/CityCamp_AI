#!/bin/bash

# Quick setup script for essential SSM parameters
# Uses actual infrastructure endpoints from Terraform

set -e

AWS_REGION="us-east-1"
PARAMETER_PREFIX="/citycamp-ai"

echo "🚀 Quick setup of essential SSM parameters for CityCamp AI..."

# Actual endpoints from Terraform output
RDS_ENDPOINT="citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com"
REDIS_ENDPOINT="citycamp-ai-redis.2gtiq7.0001.use1.cache.amazonaws.com"
DB_PASSWORD="CityCampSecure2024!"

# Construct connection URLs
DATABASE_URL="postgresql://postgres:${DB_PASSWORD}@${RDS_ENDPOINT}/citycamp_db"
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
echo "Creating placeholder parameters for optional services..."

aws ssm put-parameter \
    --name "${PARAMETER_PREFIX}/openai-api-key" \
    --value "sk-placeholder-openai-key" \
    --type "SecureString" \
    --description "OpenAI API key (placeholder - update with real key)" \
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
echo "  📝 ${PARAMETER_PREFIX}/openai-api-key (placeholder - update with real key)"
echo "  📝 ${PARAMETER_PREFIX}/twilio-* (placeholders)"
echo "  📝 ${PARAMETER_PREFIX}/smtp-* (placeholders)"
echo ""
echo "⚠️  IMPORTANT: Update the OpenAI API key with your real key:"
echo "   aws ssm put-parameter --name '${PARAMETER_PREFIX}/openai-api-key' --value 'your-real-openai-key' --type 'SecureString' --overwrite --region ${AWS_REGION}"
echo ""
echo "🚀 Your ECS deployment should now work!"
echo "   Run: aws ecs update-service --cluster citycamp-ai-cluster --service citycamp-ai-service --force-new-deployment --region ${AWS_REGION}"
