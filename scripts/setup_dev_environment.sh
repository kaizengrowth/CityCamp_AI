#!/bin/bash

# Development Environment Setup Script
# This creates a .env file for backend development with all necessary variables

echo "🔧 Setting up development environment with Twilio SMS support..."

cat > backend/.env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://citycamp_user:CityCamp2005%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/postgres
DATABASE_HOST=citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com
DATABASE_PORT=5432
DATABASE_NAME=postgres
DATABASE_USER=citycamp_user
DATABASE_PASSWORD=CityCamp2005!

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio SMS Configuration (REPLACE WITH YOUR ACTUAL VALUES!)
TWILIO_ACCOUNT_SID=your-twilio-account-sid-here
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here
TWILIO_PHONE_NUMBER=+1234567890

# Redis (for background jobs)
REDIS_URL=redis://localhost:6379/0

# Application Settings
ENVIRONMENT=development
DEBUG=true
PROJECT_NAME=CityCamp AI
PROJECT_DESCRIPTION=Tulsa Civic Engagement Platform
PROJECT_VERSION=1.0.0

# External APIs (optional - can be added later)
# OPENAI_API_KEY=your_openai_key_here
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
EOF

echo "✅ Development environment template created!"
echo "   📁 Created: backend/.env"
echo "   ⚠️  SMS notifications: DISABLED (credentials needed)"
echo "   🗄️ Database: Connected to production data"
echo ""
echo "🔐 SECURITY: Edit backend/.env and add your REAL Twilio credentials:"
echo "   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Your actual Account SID"
echo "   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   # Your actual Auth Token"
echo "   TWILIO_PHONE_NUMBER=+1234567890                      # Your actual phone number"

echo ""
echo "🚀 Next steps:"
echo "1. Edit backend/.env with real credentials"
echo "2. cd backend && python -m app.main"
echo "3. Open http://localhost:8000/docs for API docs"
echo "4. Test SMS: POST /api/v1/subscriptions/test-sms"
