#!/usr/bin/env python3
"""
Test Meeting Import Script - Local PostgreSQL Version
This script tests the meeting import functionality using local PostgreSQL
and can be easily adapted for AWS RDS once connectivity is established.
"""

import psycopg2
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

# Local PostgreSQL connection (from your docker-compose)
LOCAL_DB_CONFIG = {
    "host": "localhost",
    "port": 5435,
    "database": "citycamp_db",
    "user": "user",
    "password": "password"
}

def test_local_connection():
    """Test connection to local PostgreSQL"""
    try:
        print("🔍 Testing local PostgreSQL connection...")
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()

        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to: {version[0]}")

        # Check if meetings table exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name = 'meetings'
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM meetings")
            meeting_count = cursor.fetchone()[0]
            print(f"📊 Found {meeting_count} meetings in database")
        else:
            print("⚠️  Meetings table not found")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_sample_meeting_data() -> List[Dict]:
    """Create sample meeting data for testing"""
    return [
        {
            "title": "Test City Council Meeting - January 2024",
            "description": "Regular monthly city council meeting",
            "meeting_type": "city_council",
            "meeting_date": "2024-01-15T16:00:00",
            "location": "City Hall, Tulsa, OK",
            "meeting_url": "https://example.com/meeting-jan-15",
            "agenda_url": "https://example.com/agenda-jan-15.pdf",
            "minutes_url": "https://example.com/minutes-jan-15.pdf",
            "status": "completed",
            "external_id": "test-2024-01-15-001",
            "source": "test_import",
            "topics": ["budget", "infrastructure", "zoning"],
            "keywords": ["budget approval", "road maintenance", "zoning variance"],
            "summary": "Monthly city council meeting discussing budget and infrastructure."
        },
        {
            "title": "Test Planning Commission Meeting - January 2024",
            "description": "Planning commission review session",
            "meeting_type": "planning_commission",
            "meeting_date": "2024-01-20T14:00:00",
            "location": "Planning Department, Tulsa, OK",
            "meeting_url": "https://example.com/meeting-jan-20",
            "agenda_url": "https://example.com/agenda-jan-20.pdf",
            "minutes_url": None,
            "status": "scheduled",
            "external_id": "test-2024-01-20-002",
            "source": "test_import",
            "topics": ["development", "permits"],
            "keywords": ["development permits", "zoning review"],
            "summary": "Planning commission meeting for development permit reviews."
        }
    ]

def import_sample_meetings():
    """Import sample meetings to local database"""
    try:
        print("\n📥 Starting sample meeting import...")
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()

        meetings = create_sample_meeting_data()
        imported_count = 0

        for meeting in meetings:
            try:
                # Check if meeting already exists
                cursor.execute(
                    "SELECT id FROM meetings WHERE external_id = %s",
                    (meeting["external_id"],)
                )

                if cursor.fetchone():
                    print(f"⏭️  Skipping existing meeting: {meeting['title']}")
                    continue

                # Insert new meeting
                insert_query = """
                    INSERT INTO meetings (
                        title, description, meeting_type, meeting_date, location,
                        meeting_url, agenda_url, minutes_url, status, external_id,
                        source, topics, keywords, summary, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """

                now = datetime.now()
                cursor.execute(insert_query, (
                    meeting["title"],
                    meeting["description"],
                    meeting["meeting_type"],
                    meeting["meeting_date"],
                    meeting["location"],
                    meeting["meeting_url"],
                    meeting["agenda_url"],
                    meeting["minutes_url"],
                    meeting["status"],
                    meeting["external_id"],
                    meeting["source"],
                    json.dumps(meeting["topics"]),
                    json.dumps(meeting["keywords"]),
                    meeting["summary"],
                    now,
                    now
                ))

                imported_count += 1
                print(f"✅ Imported: {meeting['title']}")

            except Exception as e:
                print(f"❌ Failed to import {meeting['title']}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n🎉 Successfully imported {imported_count} meetings!")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_import():
    """Verify the imported meetings"""
    try:
        print("\n🔍 Verifying imported meetings...")
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, meeting_type, meeting_date, status
            FROM meetings
            WHERE source = 'test_import'
            ORDER BY meeting_date DESC
        """)

        meetings = cursor.fetchall()

        if meetings:
            print(f"📋 Found {len(meetings)} test meetings:")
            for meeting in meetings:
                title, meeting_type, meeting_date, status = meeting
                print(f"  • {title} ({meeting_type}) - {meeting_date} [{status}]")
        else:
            print("⚠️  No test meetings found")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 CityCamp AI - Meeting Import Test")
    print("=" * 50)

    # Test connection
    if not test_local_connection():
        print("\n❌ Cannot connect to local database. Please ensure:")
        print("   1. Docker containers are running (docker-compose up)")
        print("   2. PostgreSQL is available on localhost:5435")
        sys.exit(1)

    # Import sample data
    if not import_sample_meetings():
        sys.exit(1)

    # Verify import
    if not verify_import():
        sys.exit(1)

    print("\n✅ Import test completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Fix RDS connectivity (use AWS Console to make RDS publicly accessible)")
    print("   2. Update this script with RDS connection details")
    print("   3. Run import against AWS RDS")

if __name__ == "__main__":
    main()
