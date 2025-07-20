# 🔐 Secure Twilio SMS Setup Guide

## ⚠️ Security Warning

**NEVER** commit Twilio credentials to git! Your Auth Token is like a password and can be used to:
- Send SMS messages (costing you money)
- Access your Twilio account
- Send spam from your number

## 📱 Setup Steps

### 1. Get Your Twilio Credentials

From your [Twilio Console](https://console.twilio.com/):
- **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (starts with "AC", 34 chars)
- **Auth Token**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (32 character secret - keep this safe!)
- **Phone Number**: `+1234567890` (your SMS-enabled number)

### 2. Development Setup

**Option A: Environment Variables (Recommended)**
```bash
# Set these in your shell before running (USE YOUR ACTUAL VALUES!)
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_PHONE_NUMBER="+1234567890"

# Then run backend
cd backend && python -m app.main
```

**Option B: Local .env File (Secure)**
```bash
# Create backend/.env (this is gitignored)
cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://citycamp_user:CityCamp2005%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/postgres

# Security
SECRET_KEY=dev-secret-key-change-in-production

# Twilio SMS (REPLACE WITH YOUR VALUES!)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Application
ENVIRONMENT=development
DEBUG=true
EOF
```

### 3. Production Setup

**For AWS deployment:**
```bash
# Set environment variables, then deploy (USE YOUR ACTUAL VALUES!)
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_PHONE_NUMBER="+1234567890"

source scripts/setup_aws_environment_basic.sh
./aws/scripts/deploy.sh
```

### 4. Test SMS

```bash
# Test SMS endpoint
curl -X POST "http://localhost:8000/api/v1/subscriptions/test-sms" \
  -d "phone_number=+1234567890" \
  -d "test_message=Hello from CityCamp AI!"
```

## 🛡️ Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Rotate tokens regularly** - Generate new auth tokens monthly
3. **Limit access** - Only share with necessary team members
4. **Monitor usage** - Check Twilio usage logs for unusual activity
5. **Use different credentials** for dev/staging/production

## 🚨 If Credentials Are Exposed

If you accidentally commit credentials to git:

1. **Immediately rotate** your Twilio Auth Token
2. **Remove from git history**:
   ```bash
   # Remove sensitive file from git history
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch backend/.env' \
   --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (if safe to do so)
4. **Notify team members** to pull fresh

## 📞 SMS Features Enabled

- ✅ Meeting notifications 24hrs in advance
- ✅ Topic-based targeting (22 topics available)
- ✅ Phone verification for signups
- ✅ Test SMS endpoint for verification
- ✅ Delivery tracking and logs
