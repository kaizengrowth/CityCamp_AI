#!/bin/bash

# Script to connect development environment to production database
# ⚠️  WARNING: This connects dev directly to production data!

echo "⚠️  WARNING: This will connect your development environment to PRODUCTION database!"
echo "   - Any changes in development will affect production data"
echo "   - This can be risky for data integrity"
echo "   - Consider using staging environment instead"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    echo "❌ Aborted."
    exit 1
fi

# Create .env file for backend to use production database
echo "🔧 Creating backend/.env with production database connection..."

cat > backend/.env << 'EOF'
# Database - PRODUCTION CONNECTION
DATABASE_URL=postgresql://citycamp_user:CityCamp2005%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/postgres
DATABASE_HOST=citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=citycamp_user
DATABASE_PASSWORD=CityCamp2005!

# Redis - Keep local for development
REDIS_URL=redis://localhost:6382/0

# Security
SECRET_KEY=dev-secret-key-not-for-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# External APIs (add your development keys)
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# AWS (if needed for development)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket
EOF

echo "✅ Development environment now configured to use production database"
echo ""
echo "📝 Next steps:"
echo "   1. Stop current containers: docker-compose down"
echo "   2. Start only Redis: docker-compose up redis -d"
echo "   3. Run backend locally: cd backend && python -m app.main"
echo "   4. Or modify docker-compose to skip local postgres"
echo ""
echo "⚠️  Remember: Changes in dev will affect production users!"
