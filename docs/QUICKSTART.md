# CityCamp AI - Quick Start Guide

## Dependencies Fixed

The dependency conflicts have been resolved. Your CityCamp AI project is now ready for development!

## Quick Start

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

## What Was Fixed

### Dependencies Resolved
- **FastAPI**: Updated to 0.111.0 (compatible with existing packages)
- **Pydantic**: Updated to 2.9.2 (meets requirements)
- **Pydantic Settings**: Updated to 2.6.0 (compatible)
- **SQLAlchemy**: Installed 2.0.23 (database ORM)
- **PostgreSQL**: Installed psycopg2-binary (database adapter)
- **Authentication**: Installed python-jose and passlib (JWT & passwords)

### Environment Setup
- **Virtual Environment**: Created in `backend/venv/`
- **Environment Variables**: Created `.env` file from template
- **Database**: PostgreSQL ready via Docker
- **Redis**: Ready for Celery task queue

## Access Your Application

Once started, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Database**: PostgreSQL on port 5432
- **Redis**: Redis on port 6379

## Development Features

### Real-time Development
- **Hot Reload**: Backend automatically restarts on code changes
- **Live Updates**: Frontend hot-reloads on save
- **Error Display**: Clear error messages in console and browser

### Available Commands
```bash
# Run tests
cd backend && python -m pytest

# Create database migration
cd backend && alembic revision --autogenerate -m "description"

# Apply migrations
cd backend && alembic upgrade head

# Reset database (development only)
docker-compose down postgres && docker-compose up -d postgres
```

## Project Structure

```
CityCamp_AI/
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   ├── alembic/          # Database migrations
│   ├── venv/             # Virtual environment
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
├── docker-compose.yml    # Local development services
└── scripts/              # Development utilities
```

## Next Steps

### For New Developers
1. **Explore the API**: Visit http://localhost:8000/docs
2. **Check the Database**: Use your preferred PostgreSQL client
3. **Review Code Structure**: Start in `backend/app/main.py`
4. **Run Tests**: Execute `pytest` to ensure everything works

### For Existing Developers
1. **Pull Latest Changes**: Your environment should work immediately
2. **Check Dependencies**: Run `pip check` to verify no conflicts
3. **Update Database**: Run migrations if schema changed

## Troubleshooting

### Common Issues
- **Port Conflicts**: Check if ports 8000, 5432, or 6379 are in use
- **Docker Issues**: Ensure Docker is running and accessible
- **Python Version**: Ensure you're using Python 3.9+
- **Virtual Environment**: Make sure it's activated before running commands

### Quick Fixes
```bash
# Kill processes on required ports
sudo lsof -ti :8000 | xargs kill -9
sudo lsof -ti :5432 | xargs kill -9
sudo lsof -ti :6379 | xargs kill -9

# Rebuild virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review error messages in console output
3. Ensure all dependencies are properly installed
4. Check Docker service status

---

**Note**: This project uses PostgreSQL and Redis via Docker. Ensure Docker is running before starting development.
