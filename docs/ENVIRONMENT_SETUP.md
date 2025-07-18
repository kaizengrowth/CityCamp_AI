# Environment Variables Setup Guide

This guide explains how to properly configure environment variables for different environments in CityCamp AI.

## 📁 Environment Files Structure

```
CityCamp_AI/
├── backend/
│   ├── env.example       # ✅ Template for backend environment variables
│   └── .env              # 🔒 Your local backend environment (gitignored)
├── .env.production       # 🔒 Production secrets (gitignored, AWS deployment)
└── .env.local           # 🔒 Local overrides (gitignored, optional)
```

## 🎯 Purpose of Each File

### **`backend/env.example`** ✅ **Template (Committed)**
- 📝 **Template** for all environment variables needed
- 🔍 **Shows structure** and required variables
- 🚀 **Safe to commit** - contains no real secrets
- 🎯 **Use for**: Understanding what variables are needed

### **`backend/.env`** 🔒 **Local Development (Not Committed)**
- 🏠 **Your local development** environment
- 🔐 **Contains real secrets** for local testing
- 🚫 **Never committed** to Git (gitignored)
- 🎯 **Use for**: Local development and testing

### **`.env.production`** 🔒 **Production Secrets (Not Committed)**
- ☁️ **Production environment** variables
- 🔐 **Contains real production secrets**
- 🚫 **Never committed** to Git (gitignored)
- 🎯 **Use for**: AWS deployment scripts

### **`.env.local`** 🔒 **Local Overrides (Optional)**
- 🔧 **Override specific variables** locally
- 🔐 **Can contain secrets**
- 🚫 **Never committed** to Git (gitignored)
- 🎯 **Use for**: Personal development preferences

## 🚀 Quick Setup

### 1. **Local Development Setup**

```bash
# Copy the template
cp backend/env.example backend/.env

# Edit with your local values
nano backend/.env
```

**Required for local development:**
```bash
# Database (local Docker)
DATABASE_URL=postgresql://user:password@localhost:5435/citycamp_db

# Security
SECRET_KEY=your-local-secret-key-here

# Optional: External APIs for testing
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
```

### 2. **Production Setup**

```bash
# Copy template for production
cp backend/env.example .env.production

# Edit with production values
nano .env.production
```

**Required for production:**
```bash
# Database (AWS RDS)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/citycamp_db

# Security (generate strong key)
SECRET_KEY=your-super-secure-production-key

# AWS
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# External APIs
OPENAI_API_KEY=your-production-openai-key
TWILIO_ACCOUNT_SID=your-production-twilio-sid
```

## 🔐 Security Best Practices

### **✅ DO:**
- ✅ **Use strong, unique secrets** for each environment
- ✅ **Keep `.env` files gitignored**
- ✅ **Use different API keys** for dev/prod
- ✅ **Rotate secrets regularly**
- ✅ **Use AWS Parameter Store** for production secrets
- ✅ **Document required variables** in `env.example`

### **❌ DON'T:**
- ❌ **Never commit real secrets** to Git
- ❌ **Don't use production secrets** in development
- ❌ **Don't share `.env` files** via email/chat
- ❌ **Don't hardcode secrets** in source code
- ❌ **Don't use weak passwords**

## 🌍 Environment-Specific Configuration

### **Development Environment**
```bash
# backend/.env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5435/citycamp_db
CORS_ORIGINS=["http://localhost:3002"]
```

### **Production Environment**
```bash
# .env.production
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/citycamp_db
CORS_ORIGINS=["https://d1s9nkkr0t3pmn.cloudfront.net"]
```

### **Testing Environment**
```bash
# For CI/CD (GitHub Actions)
ENVIRONMENT=test
DEBUG=False
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db
SECRET_KEY=test-secret-key
```

## 🔧 Using Environment Variables

### **In Python (Backend)**
```python
from app.core.config import Settings

settings = Settings()
print(settings.database_url)  # Automatically loads from .env
```

### **In Docker Compose**
```yaml
services:
  backend:
    env_file:
      - backend/.env  # Loads environment variables
```

### **In GitHub Actions**
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

## 🚨 Troubleshooting

### **"Environment variable not found"**
1. Check if `.env` file exists in the right location
2. Verify variable name spelling
3. Ensure no spaces around `=` in `.env` file
4. Restart your application after changes

### **"Database connection failed"**
1. Check `DATABASE_URL` format
2. Verify database is running (Docker: `docker-compose up postgres`)
3. Test connection: `psql $DATABASE_URL`

### **"AWS credentials not found"**
1. Check `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
2. Verify IAM permissions
3. Test: `aws sts get-caller-identity`

## 📋 Environment Variables Reference

### **Required Variables**
| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing | `your-secret-key-here` |
| `ENVIRONMENT` | App environment | `development`/`production` |

### **Optional Variables**
| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | AI features | `sk-...` |
| `TWILIO_ACCOUNT_SID` | SMS notifications | `AC...` |
| `AWS_ACCESS_KEY_ID` | AWS services | `AKIA...` |
| `REDIS_URL` | Caching | `redis://localhost:6379/0` |

## 🔄 Migration from Old Setup

If you have multiple `.env` files, consolidate them:

```bash
# Remove duplicates
rm .env.production.template  # Use backend/env.example instead

# Standardize locations
mv .env.production .env.production  # Keep in root for deployment scripts
mv backend/.env backend/.env        # Keep backend-specific in backend/
```

---

**Remember**: Environment files contain secrets - keep them secure and never commit them to Git!
