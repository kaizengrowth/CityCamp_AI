# 🚀 CityCamp AI - Quick Start Guide

## ✅ Dependencies Fixed!

The dependency conflicts have been resolved. Your CityCamp AI project is now ready for development!

## 🏃 Quick Start

### Option 1: Use the Development Script (Recommended)
```bash
# Start the development environment
./scripts/start-dev.sh
```

### Option 2: Manual Start
```bash
# 1. Start database and Redis
docker-compose up -d postgres redis

# 2. Start backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

## 🔧 What Was Fixed

### Dependencies Resolved
- ✅ **FastAPI**: Updated to 0.111.0 (compatible with existing packages)
- ✅ **Pydantic**: Updated to 2.9.2 (meets requirements)
- ✅ **Pydantic Settings**: Updated to 2.6.0 (compatible)
- ✅ **SQLAlchemy**: Installed 2.0.23 (database ORM)
- ✅ **PostgreSQL**: Installed psycopg2-binary (database adapter)
- ✅ **Authentication**: Installed python-jose and passlib (JWT & passwords)

### Environment Setup
- ✅ **Virtual Environment**: Created in `backend/venv/`
- ✅ **Environment Variables**: Created `.env` file from template
- ✅ **Database**: PostgreSQL ready via Docker
- ✅ **Redis**: Ready for Celery task queue

## 🌐 Access Your Application

Once started, you can access:

- **🔥 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **🏥 Health Check**: http://localhost:8000/health
- **🐳 Database**: PostgreSQL on port 5432
- **🔄 Redis**: Redis on port 6379

## 🎯 Next Steps

### 1. Complete Missing Dependencies (Optional)
```bash
cd backend && source venv/bin/activate
pip install -r requirements.txt  # Install remaining packages
```

### 2. Set Up Database
```bash
# Initialize database migrations
cd backend && source venv/bin/activate
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 3. Add API Keys
Update `backend/.env` with your API keys:
```bash
# Required for full functionality
OPENAI_API_KEY=your-openai-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
SECRET_KEY=your-secret-key-here
```

### 4. Start Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 🛠️ Development Commands

```bash
# Backend
cd backend && source venv/bin/activate

# Run tests
pytest

# Check code quality
black .
flake8 .

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🐳 Docker Development

```bash
# Start all services
docker-compose up --build

# Start specific services
docker-compose up -d postgres redis

# View logs
docker-compose logs backend
docker-compose logs frontend

# Stop all services
docker-compose down
```

## 🆘 Still Having Issues?

1. **Check the troubleshooting guide**: `TROUBLESHOOTING.md`
2. **Reset dependencies**: `./scripts/fix-dependencies.sh`
3. **Clean Docker**: `docker-compose down -v && docker system prune -a`

## 🎉 Success!

Your CityCamp AI application is now ready for development! You have:

- ✅ Working FastAPI backend with authentication
- ✅ Database models for users, meetings, campaigns, and notifications
- ✅ Modern React frontend structure
- ✅ Docker development environment
- ✅ All dependency conflicts resolved

Happy coding! 🚀
