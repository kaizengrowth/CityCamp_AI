#!/usr/bin/env python3
"""
Reprocess All Production Meetings with Enhanced AI
Reprocess all meeting PDFs in production with enhanced GPT-4 AI to get better results
"""

import os
import sys
import argparse
import json
import psycopg2
from pathlib import Path
from typing import List, Dict, Any

def reprocess_production_meetings_direct(
    aws_db_url: str,
    openai_api_key: str = None,
    limit: int = None, 
    dry_run: bool = True,
    process_ai: bool = True
):
    """Reprocess all production meetings with enhanced AI using direct database connection"""
    
    print("🚀 Reprocessing All Production Meetings with Enhanced AI")
    print("=" * 70)
    
    print(f"🔗 Using AWS Database: {aws_db_url.split('@')[1] if '@' in aws_db_url else 'configured'}")
    
    # Check OpenAI API key
    if process_ai:
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
            print("🤖 OpenAI API key configured")
        elif os.environ.get('OPENAI_API_KEY'):
            print("🤖 Using existing OpenAI API key from environment")
        else:
            print("❌ OpenAI API key not provided. AI processing will be limited.")
            print("   Use --openai-key YOUR_KEY or set OPENAI_API_KEY environment variable")
            if not dry_run:
                return
    
    try:
        # Connect directly to PostgreSQL
        conn = psycopg2.connect(aws_db_url)
        cur = conn.cursor()
        
        # Get meetings with PDFs
        query = """
            SELECT id, title, meeting_date, minutes_url, summary, detailed_summary, keywords, voting_records
            FROM meetings 
            WHERE minutes_url IS NOT NULL
            ORDER BY meeting_date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        cur.execute(query)
        meetings = cur.fetchall()
        
        if not meetings:
            print("❌ No meetings with PDFs found")
            return
            
        print(f"📋 Found {len(meetings)} meetings with PDFs to process")
        print(f"🔍 Mode: {'DRY RUN' if dry_run else 'LIVE PROCESSING'}")
        print(f"🤖 AI Processing: {'ENABLED' if process_ai else 'DISABLED'}")
        print()
        
        successful_updates = 0
        skipped_no_pdf = 0
        error_count = 0
        ai_processing_count = 0
        
        for i, meeting_data in enumerate(meetings, 1):
            mid, title, meeting_date, minutes_url, summary, detailed_summary, keywords, voting_records = meeting_data
            
            print(f"🔍 [{i}/{len(meetings)}] Processing: {title}")
            print(f"   📅 Date: {meeting_date}")
            print(f"   📄 PDF: {minutes_url}")
            print(f"   🆔 ID: {mid}")
            
            try:
                # Construct full PDF path
                pdf_path = Path("backend") / minutes_url
                if not pdf_path.exists():
                    print(f"   ⚠️  PDF file not found: {pdf_path}")
                    skipped_no_pdf += 1
                    continue
                
                # Show current status
                has_summary = bool(summary and summary.strip())
                has_detailed_summary = bool(detailed_summary and detailed_summary.strip())
                has_voting_records = bool(voting_records and str(voting_records) not in ['[]', 'null'])
                keyword_count = len(keywords) if keywords else 0
                
                print(f"   📊 Current Status:")
                print(f"      Summary: {'✅' if has_summary else '❌'}")
                print(f"      Detailed Summary: {'✅' if has_detailed_summary else '❌'}")
                print(f"      Voting Records: {'✅' if has_voting_records else '❌'}")
                print(f"      Keywords: {keyword_count} {'⚠️ (too many)' if keyword_count > 10 else '✅' if keyword_count > 0 else '❌'}")
                
                # Process with enhanced AI if enabled
                if process_ai and os.environ.get('OPENAI_API_KEY'):
                    print("   🤖 Processing with Enhanced AI (GPT-4)...")
                    
                    # Import AI services here to avoid connection issues
                    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
                    from app.services.ai_categorization_service import AICategorization
                    
                    # Initialize AI service (it will pick up the API key from environment)
                    ai_service = AICategorization()
                    
                    # Read PDF content
                    with open(pdf_path, 'rb') as f:
                        pdf_content = f.read()
                    
                    # Create a mock database session for the AI service
                    class MockDB:
                        def commit(self): pass
                        def rollback(self): pass
                    
                    mock_db = MockDB()
                    
                    # Process with enhanced AI
                    processed_content = ai_service.process_meeting_minutes(
                        pdf_content, mid, mock_db
                    )
                    
                    ai_processing_count += 1
                    
                    # Show improvements
                    print(f"   ✨ AI Results:")
                    print(f"      Categories: {len(processed_content.categories)}")
                    print(f"      Keywords: {len(processed_content.keywords)} (focused ✅)")
                    print(f"      Summary Length: {len(processed_content.summary)} chars")
                    print(f"      Detailed Summary: {'✅' if processed_content.detailed_summary else '❌'}")
                    print(f"      Voting Records: {len(processed_content.voting_records)}")
                    print(f"      Vote Statistics: {processed_content.vote_statistics}")
                    
                    if not dry_run:
                        # Update the meeting with enhanced AI results
                        voting_records_json = []
                        if processed_content.voting_records:
                            voting_records_json = [vote.dict() for vote in processed_content.voting_records]
                        
                        update_query = """
                            UPDATE meetings SET
                                summary = %s,
                                detailed_summary = %s,
                                keywords = %s,
                                topics = %s,
                                voting_records = %s,
                                vote_statistics = %s
                            WHERE id = %s
                        """
                        
                        cur.execute(update_query, (
                            processed_content.summary,
                            processed_content.detailed_summary,
                            json.dumps(processed_content.keywords),
                            json.dumps(processed_content.categories),
                            json.dumps(voting_records_json),
                            json.dumps(processed_content.vote_statistics),
                            mid
                        ))
                        
                        conn.commit()
                        print(f"   ✅ Updated meeting #{mid} in database")
                        successful_updates += 1
                    else:
                        print(f"   🔍 Would update meeting #{mid} (dry run)")
                else:
                    if not process_ai:
                        print("   ⏭️  Skipping AI processing (disabled)")
                    else:
                        print("   ⏭️  Skipping AI processing (no API key)")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error processing meeting: {str(e)}")
                error_count += 1
                continue
        
        # Final Summary
        print("📊 Processing Summary:")
        print(f"   Total meetings found: {len(meetings)}")
        print(f"   PDFs processed: {ai_processing_count if process_ai else 'N/A (AI disabled)'}")
        print(f"   Successfully updated: {successful_updates if not dry_run else 'N/A (dry run)'}")
        print(f"   Skipped (no PDF): {skipped_no_pdf}")
        print(f"   Errors: {error_count}")
        
        if dry_run:
            print("\n🔍 This was a dry run. Use --apply to make changes.")
        elif process_ai:
            print(f"\n✅ Enhanced AI processing complete! Updated {successful_updates} meetings.")
        
        print("\n🎯 Enhanced AI Features:")
        print("   • GPT-4 processing for higher accuracy")
        print("   • Cleaner, focused summaries (2-3 sentences)")
        print("   • Reduced keyword noise (5-8 focused terms)")
        print("   • Structured detailed summaries with bullet points")
        print("   • Voting record extraction with member names")
        print("   • Enhanced vote statistics and categorization")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error in production meeting reprocessing: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Reprocess all production meetings with enhanced AI")
    parser.add_argument("--aws-db-url", type=str, 
                       default="postgresql://citycamp_user:REDACTED_PASSWORD@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/citycamp_db",
                       help="AWS RDS database URL")
    parser.add_argument("--openai-key", type=str, help="OpenAI API key for enhanced AI processing")
    parser.add_argument("--limit", type=int, help="Limit number of meetings to process")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI processing (just analyze)")
    
    args = parser.parse_args()
    
    # Validate AWS DB URL if provided
    if args.aws_db_url and not args.aws_db_url.startswith('postgresql://'):
        print("❌ Error: AWS DB URL should start with 'postgresql://'")
        sys.exit(1)
    
    reprocess_production_meetings_direct(
        aws_db_url=args.aws_db_url,
        openai_api_key=args.openai_key,
        limit=args.limit,
        dry_run=not args.apply,
        process_ai=not args.no_ai
    )


if __name__ == "__main__":
    main() 