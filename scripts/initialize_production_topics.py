#!/usr/bin/env python3
"""
Initialize Notification Topics in Production Database

This script initializes the default notification topics in the production PostgreSQL database.
Run this after deployment to ensure users can subscribe to meeting notifications.

Usage:
    python scripts/initialize_production_topics.py
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import asyncio
import logging
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.services.notification_service import NotificationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def initialize_topics():
    """Initialize notification topics in production database"""
    try:
        print("🏛️ Initializing notification topics in production database...")

        # Get settings and create notification service
        settings = get_settings()
        notification_service = NotificationService(settings)

        # Create database session
        with SessionLocal() as db:
            # Initialize default topics
            topics_created = await notification_service.initialize_default_topics(db)

            if topics_created > 0:
                print(f"✅ Successfully created {topics_created} notification topics!")
            else:
                print("✅ All notification topics already exist.")

            # Verify topics were created
            from app.models.subscription import MeetingTopic
            total_topics = db.query(MeetingTopic).filter(MeetingTopic.is_active == True).count()
            print(f"📊 Total active topics in database: {total_topics}")

            return topics_created

    except Exception as e:
        logger.error(f"❌ Error initializing topics: {e}")
        print(f"❌ Failed to initialize topics: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 CityCamp AI - Production Topic Initialization")
    print("=" * 50)

    # Check if we're in production environment
    database_url = os.getenv("DATABASE_URL", "")
    if "localhost" in database_url or "127.0.0.1" in database_url:
        print("⚠️  Warning: This appears to be a local database")
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Cancelled by user")
            return

    # Initialize topics
    result = await initialize_topics()

    if result is not False:
        print("\n🎉 Topic initialization completed successfully!")
        print("\nNext steps:")
        print("1. Test the topics endpoint: GET /api/v1/subscriptions/topics")
        print("2. Verify topics appear in the frontend notification signup")
        print("3. Check that users can now subscribe to meeting notifications")
    else:
        print("\n❌ Topic initialization failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
