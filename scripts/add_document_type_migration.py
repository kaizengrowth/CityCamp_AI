#!/usr/bin/env python3
"""
Database migration to add document_type field to meetings table
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import psycopg2
from app.core.config import settings

def run_migration(database_url=None):
    """Add document_type field to meetings table"""

    print("🔄 Adding document_type field to meetings table...")

    try:
        # Connect to database
        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(settings.DATABASE_URL)

        cur = conn.cursor()

        # Check if column already exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name='document_type';
        """)

        if cur.fetchone():
            print("✅ document_type column already exists")
        else:
            # Add the column
            cur.execute("""
                ALTER TABLE meetings
                ADD COLUMN document_type VARCHAR(50);
            """)
            print("✅ Added document_type column")

        # Check if detailed_summary column exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name='detailed_summary';
        """)

        if cur.fetchone():
            print("✅ detailed_summary column already exists")
        else:
            # Add the column
            cur.execute("""
                ALTER TABLE meetings
                ADD COLUMN detailed_summary TEXT;
            """)
            print("✅ Added detailed_summary column")

        # Check if voting_records column exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name='voting_records';
        """)

        if cur.fetchone():
            print("✅ voting_records column already exists")
        else:
            # Add the column
            cur.execute("""
                ALTER TABLE meetings
                ADD COLUMN voting_records JSON DEFAULT '[]';
            """)
            print("✅ Added voting_records column")

        # Check if vote_statistics column exists
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name='vote_statistics';
        """)

        if cur.fetchone():
            print("✅ vote_statistics column already exists")
        else:
            # Add the column
            cur.execute("""
                ALTER TABLE meetings
                ADD COLUMN vote_statistics JSON DEFAULT '{}';
            """)
            print("✅ Added vote_statistics column")

        # Set default values for existing records
        cur.execute("""
            UPDATE meetings
            SET document_type = CASE
                WHEN meeting_type = 'regular_council' THEN 'agenda'
                WHEN source = 'tulsa_archive' THEN 'agenda'
                WHEN minutes_url IS NOT NULL AND minutes_url LIKE '%minutes%' THEN 'minutes'
                ELSE 'agenda'
            END
            WHERE document_type IS NULL;
        """)

        updated_count = cur.rowcount
        print(f"✅ Updated document_type for {updated_count} existing meetings")

        # Commit changes
        conn.commit()

        # Show updated schema
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name IN ('document_type', 'detailed_summary', 'voting_records', 'vote_statistics')
            ORDER BY column_name;
        """)

        columns = cur.fetchall()
        print("\n📋 Updated schema:")
        for col_name, data_type, nullable in columns:
            print(f"  - {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")

        # Show sample data
        cur.execute("""
            SELECT title, document_type, meeting_type, source
            FROM meetings
            ORDER BY created_at DESC
            LIMIT 5;
        """)

        sample_data = cur.fetchall()
        if sample_data:
            print("\n📋 Sample updated records:")
            for title, doc_type, meeting_type, source in sample_data:
                print(f"  - {title[:50]}... | {doc_type} | {meeting_type} | {source}")

        conn.close()
        print("\n🎉 Migration completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    # Check if we should run against AWS database
    import argparse
    parser = argparse.ArgumentParser(description='Add document_type field to meetings table')
    parser.add_argument('--aws-db-url', help='AWS RDS database URL')
    args = parser.parse_args()

    run_migration(args.aws_db_url)
