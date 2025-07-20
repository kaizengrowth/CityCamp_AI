#!/usr/bin/env python3
"""
Script to set up PostgreSQL database with tables and import meetings data
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.meeting import Meeting, AgendaItem, MeetingCategory
from app.models.user import User
from app.models.notification import Notification

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5435/citycamp_db"

def setup_database():
    """Create all database tables"""
    print("Setting up database...")
    engine = create_engine(DATABASE_URL)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

    return engine

def import_meetings_data(engine):
    """Import meetings data from JSON export file"""
    print("Importing meetings data...")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Check if we already have meetings data
        existing_count = session.query(Meeting).count()
        if existing_count > 0:
            print(f"ℹ️ Found {existing_count} existing meetings in database")
            response = input("Do you want to continue and add more data? (y/n): ")
            if response.lower() != 'y':
                print("Skipping import...")
                return

        # Load meetings from JSON file
        json_file = Path(__file__).parent.parent / "meetings_export.json"

        if not json_file.exists():
            print(f"❌ Meetings data file not found: {json_file}")
            return

        with open(json_file, 'r') as f:
            meetings_data = json.load(f)

        if isinstance(meetings_data, dict) and 'meetings' in meetings_data:
            meetings_list = meetings_data['meetings']
        else:
            meetings_list = meetings_data

        print(f"Found {len(meetings_list)} meetings to import")

        imported_count = 0
        for meeting_data in meetings_list:
            try:
                # Check if meeting already exists
                existing = session.query(Meeting).filter_by(
                    external_id=meeting_data.get('external_id')
                ).first()

                if existing:
                    continue

                # Parse meeting date
                meeting_date_str = meeting_data.get('meeting_date')
                if meeting_date_str:
                    try:
                        meeting_date = datetime.fromisoformat(meeting_date_str.replace('Z', '+00:00'))
                    except:
                        meeting_date = datetime.now()
                else:
                    meeting_date = datetime.now()

                # Create meeting record
                meeting = Meeting(
                    title=meeting_data.get('title', 'Unknown Meeting'),
                    description=meeting_data.get('description'),
                    meeting_type=meeting_data.get('meeting_type', 'city_council'),
                    meeting_date=meeting_date,
                    location=meeting_data.get('location'),
                    meeting_url=meeting_data.get('meeting_url'),
                    agenda_url=meeting_data.get('agenda_url'),
                    minutes_url=meeting_data.get('minutes_url'),
                    status=meeting_data.get('status', 'completed'),
                    external_id=meeting_data.get('external_id'),
                    source=meeting_data.get('source', 'tulsa_city_council'),
                    topics=meeting_data.get('topics', []),
                    keywords=meeting_data.get('keywords', []),
                    summary=meeting_data.get('summary')
                )

                session.add(meeting)
                imported_count += 1

                if imported_count % 10 == 0:
                    print(f"Imported {imported_count} meetings...")

            except Exception as e:
                print(f"Error importing meeting {meeting_data.get('title', 'Unknown')}: {e}")
                continue

        session.commit()
        print(f"✅ Successfully imported {imported_count} meetings!")

    except Exception as e:
        print(f"❌ Error importing meetings data: {e}")
        session.rollback()
    finally:
        session.close()

def main():
    """Main function to set up database and import data"""
    print("🚀 CityCamp AI Database Setup")
    print("="*50)

    try:
        # Setup database tables
        engine = setup_database()

        # Import meetings data
        import_meetings_data(engine)

        print("\n🎉 Database setup complete!")
        print("\nYou can now:")
        print("- Start the backend API: docker-compose up backend")
        print("- Access the database: psql postgresql://user:password@localhost:5435/citycamp_db")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
