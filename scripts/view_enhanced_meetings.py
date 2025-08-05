#!/usr/bin/env python3
"""
View Enhanced Meetings
Display enhanced meetings from production database with detailed formatting
"""

import os
import sys
import json
import psycopg2
from pathlib import Path

def view_enhanced_meetings(aws_db_url: str, meeting_ids: list = None):
    """View enhanced meetings from production database"""
    
    print("👀 Viewing Enhanced Meetings from Production Database")
    print("=" * 60)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(aws_db_url)
        cur = conn.cursor()
        
        # Query for enhanced meetings
        if meeting_ids:
            placeholders = ','.join(['%s'] * len(meeting_ids))
            query = f"""
                SELECT 
                    id, title, meeting_date, summary, detailed_summary,
                    keywords, topics, voting_records, vote_statistics
                FROM meetings 
                WHERE id IN ({placeholders})
                ORDER BY meeting_date DESC
            """
            cur.execute(query, meeting_ids)
        else:
            # Get recently enhanced meetings (ones with detailed summaries)
            query = """
                SELECT 
                    id, title, meeting_date, summary, detailed_summary,
                    keywords, topics, voting_records, vote_statistics
                FROM meetings 
                WHERE detailed_summary IS NOT NULL 
                AND detailed_summary != ''
                ORDER BY meeting_date DESC
                LIMIT 10
            """
            cur.execute(query)
        
        meetings = cur.fetchall()
        
        if not meetings:
            print("❌ No enhanced meetings found")
            return
            
        print(f"📋 Found {len(meetings)} enhanced meetings")
        print()
        
        for i, meeting_data in enumerate(meetings, 1):
            mid, title, meeting_date, summary, detailed_summary, keywords, topics, voting_records, vote_statistics = meeting_data
            
            print(f"{'='*80}")
            print(f"🎯 MEETING #{mid} ({i}/{len(meetings)})")
            print(f"{'='*80}")
            print(f"📅 **Date**: {meeting_date}")
            print(f"📋 **Title**: {title}")
            print()
            
            # Parse JSON fields (handle both string and already-parsed formats)
            def safe_parse_json(data):
                if data is None:
                    return None
                if isinstance(data, (list, dict)):
                    return data  # Already parsed
                if isinstance(data, str):
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        return None
                return None
            
            keywords_list = safe_parse_json(keywords) or []
            topics_list = safe_parse_json(topics) or []
            voting_records_list = safe_parse_json(voting_records) or []
            vote_stats = safe_parse_json(vote_statistics) or {}
            
            # Display enhanced summary
            print("📝 **ENHANCED SUMMARY**:")
            print(f"   {summary}")
            print()
            
            # Display detailed summary
            if detailed_summary:
                print("📋 **DETAILED SUMMARY**:")
                # Format the detailed summary nicely
                detailed_lines = detailed_summary.split('\n')
                for line in detailed_lines:
                    if line.strip():
                        if line.startswith('**') and line.endswith(':**'):
                            print(f"   🔸 {line}")
                        elif line.startswith('• '):
                            print(f"     {line}")
                        else:
                            print(f"   {line}")
                print()
            
            # Display categories
            if topics_list:
                print("🏷️ **CATEGORIES**:")
                for topic in topics_list:
                    print(f"   • {topic}")
                print()
            
            # Display keywords
            if keywords_list:
                print("🔤 **FOCUSED KEYWORDS**:")
                keyword_str = ", ".join(keywords_list)
                print(f"   {keyword_str}")
                print(f"   📊 Count: {len(keywords_list)} (much cleaner!)")
                print()
            
            # Display voting records
            if voting_records_list:
                print("🗳️ **VOTING RECORDS**:")
                for vote in voting_records_list:
                    if isinstance(vote, dict):
                        agenda_item = vote.get('agenda_item', 'Unknown Item')
                        council_member = vote.get('council_member', 'Unknown Member')
                        vote_choice = vote.get('vote', 'Unknown')
                        outcome = vote.get('outcome', 'Unknown')
                        
                        print(f"   📝 {agenda_item}")
                        print(f"      👤 {council_member}: {vote_choice.upper()}")
                        print(f"      📊 Outcome: {outcome.upper()}")
                        print()
            
            # Display vote statistics
            if vote_stats:
                print("📊 **VOTE STATISTICS**:")
                for stat_key, stat_value in vote_stats.items():
                    formatted_key = stat_key.replace('_', ' ').title()
                    print(f"   • {formatted_key}: {stat_value}")
                print()
            
            # Summary of improvements
            print("✨ **IMPROVEMENTS MADE**:")
            print(f"   ✅ Keywords reduced to {len(keywords_list)} focused terms")
            print(f"   ✅ Added detailed summary with bullet points")
            print(f"   ✅ Extracted {len(voting_records_list)} voting records")
            print(f"   ✅ Added {len(topics_list)} relevant categories")
            if vote_stats:
                print(f"   ✅ Generated comprehensive vote statistics")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="View enhanced meetings from production database")
    parser.add_argument("--aws-db-url", type=str, 
                       default="postgresql://citycamp_user:CityCampSecure2024%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/citycamp_db",
                       help="AWS RDS database URL")
    parser.add_argument("--meeting-ids", type=int, nargs='+', help="Specific meeting IDs to view")
    
    args = parser.parse_args()
    
    view_enhanced_meetings(args.aws_db_url, args.meeting_ids)

if __name__ == "__main__":
    main() 