#!/usr/bin/env python3
"""Test database connection and settings"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

from app.core.config import Settings
from app.core.database import SessionLocal, engine
from sqlalchemy import text

def test_db_connection():
    """Test database connection"""
    settings = Settings()

    print("Database Configuration:")
    print(f"DATABASE_URL: {settings.database_url}")
    print(f"Database Host: {settings.database_host}")
    print(f"Database Port: {settings.database_port}")
    print(f"Database Name: {settings.database_name}")
    print(f"Database User: {settings.database_user}")
    print(f"Database Password: {settings.database_password}")
    print()

    # Check environment variables
    print("Environment Variables:")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST', 'Not set')}")
    print(f"DATABASE_PORT: {os.getenv('DATABASE_PORT', 'Not set')}")
    print(f"DATABASE_NAME: {os.getenv('DATABASE_NAME', 'Not set')}")
    print(f"DATABASE_USER: {os.getenv('DATABASE_USER', 'Not set')}")
    print(f"DATABASE_PASSWORD: {os.getenv('DATABASE_PASSWORD', 'Not set')}")
    print()

    # Test connection
    try:
        db = SessionLocal()
        print("✅ Database connection successful!")

        # Test query - use text() for SQLAlchemy 2.0 compatibility
        result = db.execute(text("SELECT 1 as test;"))
        print(f"✅ Test query successful: {result.fetchone()}")

        db.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()
