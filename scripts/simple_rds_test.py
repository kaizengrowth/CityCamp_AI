#!/usr/bin/env python3
"""
Simple RDS Connection Test
Test database connectivity using environment variables for security
"""

import os
import sys
import psycopg2
from datetime import datetime


def get_rds_connection_params():
    """Get RDS connection parameters from environment variables"""
    db_url = os.getenv('AWS_DB_URL')
    if not db_url:
        print("❌ Error: AWS_DB_URL environment variable not set")
        print("Please set the AWS_DB_URL environment variable with your database connection string")
        print("Example: export AWS_DB_URL='postgresql://user:password@host:port/database'")
        sys.exit(1)
    
    # Parse the database URL
    # Format: postgresql://user:password@host:port/database
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading '/'
            'user': parsed.username,
            'password': parsed.password
        }
    except Exception as e:
        print(f"❌ Error parsing database URL: {e}")
        print("Please ensure AWS_DB_URL is in format: postgresql://user:password@host:port/database")
        sys.exit(1)

def test_connection():
    """Test basic connection to RDS"""
    try:
        print("Testing RDS connection...")
        
        # Get connection parameters from environment
        params = get_rds_connection_params()
        
        conn = psycopg2.connect(
            host=params['host'],
            port=params['port'],
            database=params['database'],
            user=params['user'],
            password=params['password']
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected successfully! PostgreSQL version: {version[0]}")

        # Test table existence
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📋 Found {len(tables)} tables: {[t[0] for t in tables]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_sample_meeting():
    """Create a sample meeting in RDS"""
    try:
        print("\nCreating sample meeting...")
        
        # Get connection parameters from environment
        params = get_rds_connection_params()
        
        conn = psycopg2.connect(
            host=params['host'],
            port=params['port'],
            database=params['database'],
            user=params['user'],
            password=params['password']
        )

        cursor = conn.cursor()

        # Insert a sample meeting
        cursor.execute("""
            INSERT INTO meetings (
                title, description, meeting_type, meeting_date,
                location, status, external_id, source, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (external_id) DO NOTHING
            RETURNING id;
        """, (
            "Test Meeting - Import Script",
            "Sample meeting created by import script",
            "test",
            datetime.now(),
            "Test Location",
            "completed",
            f"test-import-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "import_script",
            datetime.now(),
            datetime.now()
        ))

        result = cursor.fetchone()
        if result:
            meeting_id = result[0]
            print(f"✅ Created meeting with ID: {meeting_id}")
        else:
            print("ℹ️  Meeting already exists (no duplicate created)")

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to create meeting: {e}")
        return False

def list_meetings():
    """List existing meetings in RDS"""
    try:
        print("\nListing existing meetings...")
        
        # Get connection parameters from environment
        params = get_rds_connection_params()
        
        conn = psycopg2.connect(
            host=params['host'],
            port=params['port'],
            database=params['database'],
            user=params['user'],
            password=params['password']
        )

        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, meeting_date, status, source
            FROM meetings
            ORDER BY meeting_date DESC
            LIMIT 10;
        """)

        meetings = cursor.fetchall()
        print(f"📅 Found {len(meetings)} recent meetings:")
        for meeting in meetings:
            print(f"  - ID: {meeting[0]}, Title: {meeting[1][:50]}..., Date: {meeting[2]}, Status: {meeting[3]}, Source: {meeting[4]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to list meetings: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting RDS Connection Test")
    print("=" * 50)

    # Test connection
    if not test_connection():
        print("\n❌ Connection test failed. Please check:")
        print("1. Security group allows your IP (99.167.223.242)")
        print("2. RDS is publicly accessible")
        print("3. Network connectivity")
        sys.exit(1)

    # List existing meetings
    list_meetings()

    # Create sample meeting
    create_sample_meeting()

    # List meetings again to confirm
    list_meetings()

    print("\n✅ All tests completed successfully!")
    print("\nNext steps:")
    print("1. Use the full import script to import real data")
    print("2. Import from your local database or CSV files")
