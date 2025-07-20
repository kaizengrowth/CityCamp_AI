#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def test_production_database():
    """Test production database connection"""

    # Load production environment
    env_file = Path(__file__).parent.parent / ".env.production"
    if not env_file.exists():
        print("❌ .env.production file not found!")
        print("Run: ./scripts/create_production_env.sh")
        return False

    load_dotenv(env_file)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in .env.production")
        return False

    print(f"🔗 Testing connection to: {database_url.replace(':CityCamp2005%21@', ':****@')}")

    try:
        # Create engine
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )

        # Test connection
        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ Database connection successful!")

            # Test meetings table
            result = conn.execute(text("SELECT COUNT(*) as meeting_count FROM meetings"))
            meeting_count = result.fetchone()[0]
            print(f"✅ Found {meeting_count} meetings")

            # Test new notification tables
            result = conn.execute(text("SELECT COUNT(*) as topic_count FROM meeting_topics"))
            topic_count = result.fetchone()[0]
            print(f"✅ Found {topic_count} notification topics")

            result = conn.execute(text("SELECT COUNT(*) as subscription_count FROM topic_subscriptions"))
            subscription_count = result.fetchone()[0]
            print(f"✅ Found {subscription_count} subscriptions")

        print("\n🎉 Production database is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Possible issues:")
        print("1. Password needs URL encoding: CityCamp2005! → CityCamp2005%21")
        print("2. Check if RDS instance is accessible")
        print("3. Verify database credentials")
        return False

if __name__ == "__main__":
    test_production_database()
