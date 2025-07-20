#!/bin/bash

# Create production environment file with proper URL encoding
echo "Creating .env.production file with correct database URL encoding..."

cat > .env.production << 'EOF'
# Database (URL-encoded password: CityCamp2005! becomes CityCamp2005%21)
DATABASE_URL=postgresql://citycamp_user:CityCamp2005%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/postgres
DATABASE_HOST=citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=citycamp_user
DATABASE_PASSWORD=CityCamp2005!

# Redis (make sure this points to your production Redis instance)
REDIS_URL=redis://your-redis-host:6379/0

# Security
SECRET_KEY=your-production-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=false

# External APIs (add your production keys)
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# AWS (if using)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket

# Email (if using SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-password
EOF

echo "✅ Created .env.production with URL-encoded database password"
echo "⚠️  Remember to:"
echo "   1. Update your production secret keys"
echo "   2. Set correct Redis URL"
echo "   3. Add your API keys (Twilio, OpenAI, etc.)"
echo ""
echo "🔐 Database password encoding:"
echo "   Original: CityCamp2005!"
echo "   Encoded:  CityCamp2005%21"
