# Security Setup Guide

## 🔐 Environment Variables for Database Access

**CRITICAL**: Never commit database credentials to version control. This guide explains how to securely configure database access.

## Required Environment Variables

### AWS RDS Database URL
```bash
export AWS_DB_URL="postgresql://username:password@host:port/database"
```

### OpenAI API Key (for AI processing scripts)
```bash
export OPENAI_API_KEY="sk-proj-..."
```

## Setup Instructions

### 1. Local Development

Create a `.env` file in your project root (this file is in `.gitignore`):

```bash
# .env file (DO NOT COMMIT)
AWS_DB_URL=postgresql://username:password@host:port/database
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

Load environment variables:
```bash
# For current session
source .env

# Or export individually
export AWS_DB_URL="postgresql://username:password@host:port/database"
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

### 2. Production/CI Environment

Set environment variables in your deployment environment:

**GitHub Actions:**
```yaml
env:
  AWS_DB_URL: ${{ secrets.AWS_DB_URL }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**AWS ECS/Fargate:**
```json
{
  "environment": [
    {
      "name": "AWS_DB_URL",
      "value": "postgresql://username:password@host:port/database"
    }
  ]
}
```

**Docker:**
```bash
docker run -e AWS_DB_URL="postgresql://..." your-app
```

## Script Usage

All scripts now require environment variables:

```bash
# Set the environment variable first
export AWS_DB_URL="postgresql://username:password@host:port/database"

# Then run scripts
python scripts/view_enhanced_meetings.py
python scripts/check_production_meetings.py
python scripts/reprocess_all_production_meetings.py --openai-key="sk-proj-..."
```

## Security Best Practices

### ✅ DO:
- Use environment variables for all sensitive data
- Add `.env` files to `.gitignore`
- Use GitHub Secrets for CI/CD
- Rotate credentials regularly
- Use least-privilege database users

### ❌ DON'T:
- Hardcode credentials in source code
- Commit `.env` files or credential files
- Share credentials in chat/email
- Use production credentials in development
- Log credential values

## Verification

Check that no credentials are hardcoded:
```bash
# Search for potential credential patterns
grep -r "postgresql://" scripts/ --exclude-dir=.git
grep -r "password" scripts/ --exclude-dir=.git
grep -r "secret" scripts/ --exclude-dir=.git
```

## Error Handling

If environment variables are not set, scripts will show helpful error messages:

```
❌ Error: AWS_DB_URL environment variable not set
Please set the AWS_DB_URL environment variable with your database connection string
Example: export AWS_DB_URL='postgresql://user:password@host:port/database'
```

## Migration from Hardcoded Credentials

If you previously used hardcoded credentials:

1. **Set environment variables** as described above
2. **Remove hardcoded defaults** from scripts
3. **Update documentation** to reference this security guide
4. **Test scripts** with environment variables
5. **Commit changes** (credentials are now secure)

## AWS Parameter Store (Advanced)

For production, consider using AWS Parameter Store:

```python
import boto3

def get_database_url():
    """Get database URL from AWS Parameter Store"""
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name='/citycamp/database/url',
        WithDecryption=True
    )
    return response['Parameter']['Value']
```

## Support

If you need help setting up secure credentials:
1. Check this documentation first
2. Verify environment variables are set correctly
3. Test with simple `echo $AWS_DB_URL` command
4. Contact the development team if issues persist

---

**Remember**: Security is everyone's responsibility. Always verify that sensitive data is not exposed in version control. 