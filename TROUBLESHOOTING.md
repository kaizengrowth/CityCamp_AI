# CityCamp AI - Troubleshooting Guide

## 🔧 Dependency Conflicts

### Problem
You're seeing pip dependency resolver errors like:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed...
```

### Solution

**Option 1: Use the Fix Script (Recommended)**
```bash
# Run the automated fix script
./scripts/fix-dependencies.sh
```

**Option 2: Manual Fix**
```bash
# 1. Create a fresh virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create .env file
cp env.example .env
```

**Option 3: Global Environment Reset**
If you're using a global Python environment (not recommended):
```bash
# Uninstall conflicting packages
pip uninstall prefect whisperx pendulum -y

# Install our requirements
cd backend
pip install -r requirements.txt
```

## 🐳 Docker Issues

### Problem: Docker containers won't start

**Solution:**
```bash
# Clean up Docker resources
docker-compose down -v
docker system prune -a

# Rebuild and start
docker-compose up --build
```

### Problem: Port conflicts

**Solution:**
```bash
# Check what's using the ports
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL

# Kill processes or change ports in docker-compose.yml
```

## 📊 Database Issues

### Problem: Database connection errors

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Problem: Migration errors

**Solution:**
```bash
# Initialize Alembic (if not done)
cd backend
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 🚀 Development Server Issues

### Problem: FastAPI server won't start

**Solution:**
```bash
# Check if virtual environment is activated
source venv/bin/activate

# Check Python path
echo $PYTHONPATH

# Start server with full path
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Problem: React development server issues

**Solution:**
```bash
# Clear npm cache
cd frontend
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Start development server
npm run dev
```

## 🔑 Environment Variables

### Problem: Missing API keys

**Solution:**
1. Copy the example environment file:
   ```bash
   cp backend/env.example backend/.env
   ```

2. Update the `.env` file with your actual values:
   ```bash
   # Required for development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:password@localhost/citycamp_db
   
   # Optional for full functionality
   OPENAI_API_KEY=your-openai-key
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   ```

## 🌐 Network Issues

### Problem: CORS errors

**Solution:**
Update `backend/app/core/config.py`:
```python
cors_origins: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
```

### Problem: API requests failing

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend proxy configuration
# Update frontend/vite.config.ts proxy settings
```

## 🔍 Common Error Messages

### "ModuleNotFoundError: No module named 'app'"

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Set Python path
export PYTHONPATH=/path/to/backend:$PYTHONPATH

# Or run with module flag
python -m uvicorn app.main:app --reload
```

### "pydantic.error_wrappers.ValidationError"

**Solution:**
```bash
# Update pydantic version
pip install pydantic>=2.9.0

# Or check your model definitions in app/models/
```

### "sqlalchemy.exc.OperationalError: connection to server"

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/citycamp_db
```

## 💡 Performance Issues

### Problem: Slow API responses

**Solution:**
```bash
# Enable debug mode
export DEBUG=True

# Check database query performance
# Add logging to app/core/database.py
```

### Problem: High memory usage

**Solution:**
```bash
# Limit Docker memory usage
# Add to docker-compose.yml services:
#   backend:
#     mem_limit: 512m
```

## 🛠️ Getting Help

1. **Check logs:**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Enable debug mode:**
   ```bash
   export DEBUG=True
   export PYTHONPATH=/path/to/backend
   ```

3. **Test API endpoints:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/docs
   ```

4. **Database debugging:**
   ```bash
   docker-compose exec postgres psql -U user -d citycamp_db
   ```

## 🔄 Reset Everything

If all else fails, reset the entire project:
```bash
# Stop all containers
docker-compose down -v

# Remove virtual environment
rm -rf backend/venv

# Clean Docker
docker system prune -a

# Start fresh
./scripts/fix-dependencies.sh
docker-compose up --build
``` 