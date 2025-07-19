#!/usr/bin/env python3
"""
Export Local Data to RDS-Ready Format
This script exports meeting data from local PostgreSQL to formats that can be imported to RDS
"""

import psycopg2
import json
import csv
import sys
from datetime import datetime
from typing import List, Dict

# Local PostgreSQL connection (from your docker-compose)
LOCAL_DB_CONFIG = {
    "host": "localhost",
    "port": 5435,
    "database": "citycamp_db",
    "user": "user",
    "password": "password"
}

def export_meetings_to_json():
    """Export all meetings to JSON format"""
    try:
        print("🔍 Connecting to local database...")
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()

        # Get all meetings
        cursor.execute("""
            SELECT
                title, description, meeting_type, meeting_date, location,
                meeting_url, agenda_url, minutes_url, status, external_id,
                source, topics, keywords, summary, created_at, updated_at
            FROM meetings
            ORDER BY meeting_date DESC
        """)

        meetings = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Convert to list of dictionaries
        meetings_data = []
        for meeting in meetings:
            meeting_dict = {}
            for i, value in enumerate(meeting):
                if isinstance(value, datetime):
                    meeting_dict[columns[i]] = value.isoformat()
                else:
                    meeting_dict[columns[i]] = value
            meetings_data.append(meeting_dict)

        # Save to JSON
        with open('meetings_export.json', 'w') as f:
            json.dump(meetings_data, f, indent=2, default=str)

        print(f"✅ Exported {len(meetings_data)} meetings to meetings_export.json")

        cursor.close()
        conn.close()
        return len(meetings_data)

    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 0

def export_meetings_to_csv():
    """Export all meetings to CSV format"""
    try:
        print("🔍 Connecting to local database...")
        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()

        # Get all meetings
        cursor.execute("""
            SELECT
                title, description, meeting_type, meeting_date, location,
                meeting_url, agenda_url, minutes_url, status, external_id,
                source, topics, keywords, summary, created_at, updated_at
            FROM meetings
            ORDER BY meeting_date DESC
        """)

        meetings = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Save to CSV
        with open('meetings_export.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)  # Header

            for meeting in meetings:
                # Convert datetime objects to strings
                row = []
                for value in meeting:
                    if isinstance(value, datetime):
                        row.append(value.isoformat())
                    elif value is None:
                        row.append('')
                    else:
                        row.append(str(value))
                writer.writerow(row)

        print(f"✅ Exported {len(meetings)} meetings to meetings_export.csv")

        cursor.close()
        conn.close()
        return len(meetings)

    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 0

def create_pg_dump():
    """Create a PostgreSQL dump for direct import"""
    try:
        print("🔍 Creating PostgreSQL dump...")
        import subprocess

        # Create pg_dump command
        dump_cmd = [
            'pg_dump',
            '-h', 'localhost',
            '-p', '5435',
            '-U', 'user',
            '-d', 'citycamp_db',
            '-t', 'meetings',  # Only meetings table
            '--data-only',     # Only data, not schema
            '--inserts',       # Use INSERT statements
            '-f', 'meetings_dump.sql'
        ]

        # Set password environment variable
        env = {'PGPASSWORD': 'password'}

        result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Created PostgreSQL dump: meetings_dump.sql")
            return True
        else:
            print(f"❌ pg_dump failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Dump creation failed: {e}")
        return False

def show_statistics():
    """Show database statistics"""
    try:
        print("\n📊 Database Statistics:")
        print("=" * 40)

        conn = psycopg2.connect(**LOCAL_DB_CONFIG)
        cursor = conn.cursor()

        # Total meetings
        cursor.execute("SELECT COUNT(*) FROM meetings")
        total_meetings = cursor.fetchone()[0]
        print(f"Total meetings: {total_meetings}")

        # Meetings by type
        cursor.execute("""
            SELECT meeting_type, COUNT(*)
            FROM meetings
            GROUP BY meeting_type
            ORDER BY COUNT(*) DESC
        """)
        meeting_types = cursor.fetchall()
        print("\nMeetings by type:")
        for meeting_type, count in meeting_types:
            print(f"  • {meeting_type}: {count}")

        # Meetings by status
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM meetings
            GROUP BY status
            ORDER BY COUNT(*) DESC
        """)
        statuses = cursor.fetchall()
        print("\nMeetings by status:")
        for status, count in statuses:
            print(f"  • {status}: {count}")

        # Date range
        cursor.execute("""
            SELECT MIN(meeting_date), MAX(meeting_date)
            FROM meetings
        """)
        date_range = cursor.fetchone()
        if date_range[0] and date_range[1]:
            print(f"\nDate range: {date_range[0].date()} to {date_range[1].date()}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Statistics failed: {e}")

def main():
    """Main function"""
    print("🚀 CityCamp AI - Local Data Export")
    print("=" * 50)

    # Show statistics
    show_statistics()

    print("\n📤 Exporting data...")

    # Export to different formats
    json_count = export_meetings_to_json()
    csv_count = export_meetings_to_csv()
    dump_success = create_pg_dump()

    print("\n✅ Export Summary:")
    print(f"  • JSON export: {json_count} meetings")
    print(f"  • CSV export: {csv_count} meetings")
    print(f"  • SQL dump: {'✅ Success' if dump_success else '❌ Failed'}")

    print("\n📝 Files created:")
    print("  • meetings_export.json - JSON format for import script")
    print("  • meetings_export.csv - CSV format for manual review")
    if dump_success:
        print("  • meetings_dump.sql - PostgreSQL dump for direct import")

    print("\n🔄 Next steps:")
    print("  1. Fix RDS connectivity (make it publicly accessible)")
    print("  2. Use these files to import to RDS:")
    print("     - JSON: python import_meetings_to_aws_rds.py --source json --file meetings_export.json")
    print("     - SQL: psql -h RDS_HOST -U citycamp_user -d citycamp_db -f meetings_dump.sql")

if __name__ == "__main__":
    main()
