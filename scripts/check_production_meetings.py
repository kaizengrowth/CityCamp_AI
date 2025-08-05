#!/usr/bin/env python3
"""
Check Production Meetings Status
Check the current status of meetings in production database
"""

import os
import sys
import psycopg2
from pathlib import Path

def check_production_meetings(aws_db_url: str):
    """Check current state of meetings in production"""
    
    print("🔍 Checking Production Meetings Status")
    print("=" * 50)
    
    try:
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(aws_db_url)
        cur = conn.cursor()
        
        # Get basic meeting statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_meetings,
                COUNT(CASE WHEN minutes_url IS NOT NULL THEN 1 END) as with_pdfs,
                COUNT(CASE WHEN summary IS NOT NULL AND summary != '' THEN 1 END) as with_summary,
                COUNT(CASE WHEN detailed_summary IS NOT NULL AND detailed_summary != '' THEN 1 END) as with_detailed_summary,
                COUNT(CASE WHEN voting_records IS NOT NULL AND voting_records::text != '[]' AND voting_records::text != 'null' THEN 1 END) as with_voting_records,
                COUNT(CASE WHEN keywords IS NOT NULL AND keywords::text != '[]' AND keywords::text != 'null' THEN 1 END) as with_keywords
            FROM meetings
        """)
        
        stats = cur.fetchone()
        total, with_pdfs, with_summary, with_detailed, with_voting, with_keywords = stats
        
        print(f"📊 Meeting Statistics:")
        print(f"   Total meetings: {total}")
        print(f"   With PDFs: {with_pdfs}")
        print(f"   With summary: {with_summary}")
        print(f"   With detailed summary: {with_detailed}")
        print(f"   With voting records: {with_voting}")
        print(f"   With keywords: {with_keywords}")
        print()
        
        # Get sample meetings with details
        cur.execute("""
            SELECT 
                id, title, meeting_date, meeting_type, minutes_url,
                CASE WHEN summary IS NOT NULL AND summary != '' THEN 'Yes' ELSE 'No' END as has_summary,
                CASE WHEN detailed_summary IS NOT NULL AND detailed_summary != '' THEN 'Yes' ELSE 'No' END as has_detailed,
                CASE WHEN keywords IS NOT NULL AND keywords::text != '[]' AND keywords::text != 'null' 
                     THEN array_length(string_to_array(trim(both '[]' from keywords::text), ','), 1) 
                     ELSE 0 END as keyword_count
            FROM meetings 
            WHERE minutes_url IS NOT NULL
            ORDER BY meeting_date DESC 
            LIMIT 10
        """)
        
        meetings = cur.fetchall()
        
        print(f"📋 Recent Meetings with PDFs (Last 10):")
        print(f"{'ID':<4} {'Date':<12} {'Type':<20} {'Summary':<8} {'Detailed':<9} {'Keywords':<8}")
        print("-" * 70)
        
        for meeting in meetings:
            mid, title, date, mtype, pdf, has_sum, has_det, kw_count = meeting
            print(f"{mid:<4} {str(date)[:10]:<12} {mtype[:18]:<20} {has_sum:<8} {has_det:<9} {kw_count:<8}")
        
        print()
        
        # Check for meetings that need AI processing
        cur.execute("""
            SELECT COUNT(*) 
            FROM meetings 
            WHERE minutes_url IS NOT NULL 
            AND (summary IS NULL OR summary = '' OR detailed_summary IS NULL OR detailed_summary = '')
        """)
        
        needs_processing = cur.fetchone()[0]
        print(f"🤖 Meetings needing AI processing: {needs_processing}")
        
        # Check date range
        cur.execute("""
            SELECT 
                MIN(meeting_date) as earliest,
                MAX(meeting_date) as latest,
                COUNT(DISTINCT DATE_TRUNC('year', meeting_date)) as years_covered
            FROM meetings
        """)
        
        date_range = cur.fetchone()
        earliest, latest, years = date_range
        
        print(f"📅 Date Range:")
        print(f"   Earliest: {earliest}")
        print(f"   Latest: {latest}")
        print(f"   Years covered: {years}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    aws_db_url = "postgresql://citycamp_user:REDACTED_PASSWORD@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/citycamp_db"
    check_production_meetings(aws_db_url)

if __name__ == "__main__":
    main() 