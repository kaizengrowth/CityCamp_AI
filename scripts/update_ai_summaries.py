#!/usr/bin/env python3
"""
Update AI Summaries
Reprocess existing meetings with enhanced AI to improve summary quality
"""

import os
import sys
import argparse
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.meeting import Meeting
from app.services.ai_categorization_service import AICategorization
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_ai_summaries(limit: int = 10, dry_run: bool = True):
    """Update existing meetings with enhanced AI summaries"""

    print("🤖 Updating AI Summaries with Enhanced Processing")
    print("=" * 60)

    db = SessionLocal()
    ai_service = AICategorization()

    try:
        # Get meetings that have PDFs but need better summaries
        query = (
            db.query(Meeting)
            .filter(Meeting.minutes_url.isnot(None))
            .order_by(Meeting.meeting_date.desc())
        )

        if limit:
            query = query.limit(limit)

        meetings = query.all()

        if not meetings:
            print("❌ No meetings with PDFs found")
            return

        print(f"📋 Processing {len(meetings)} meetings...")
        print(f"🔍 Mode: {'DRY RUN' if dry_run else 'LIVE UPDATE'}")
        print()

        updated_count = 0
        error_count = 0

        for i, meeting in enumerate(meetings, 1):
            print(f"🔍 [{i}/{len(meetings)}] {meeting.title}")
            print(f"   Date: {meeting.meeting_date}")
            print(f"   PDF: {meeting.minutes_url}")

            try:
                # Construct full PDF path
                pdf_path = Path("backend") / meeting.minutes_url
                if not pdf_path.exists():
                    print(f"   ❌ PDF file not found: {pdf_path}")
                    error_count += 1
                    continue

                # Read PDF content
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()

                # Process with enhanced AI
                print("   🤖 Processing with enhanced AI...")
                processed_content = ai_service.process_meeting_minutes(
                    pdf_content, meeting.id, db
                )

                # Show comparison
                old_summary = meeting.summary[:100] if meeting.summary else "None"
                new_summary = processed_content.summary[:100]

                print(f"   📝 Old Summary: {old_summary}...")
                print(f"   📝 New Summary: {new_summary}...")

                # Show improvements
                improvements = []
                if len(processed_content.keywords) < 10:
                    improvements.append(f"Keywords reduced to {len(processed_content.keywords)}")
                if processed_content.voting_records:
                    improvements.append(f"{len(processed_content.voting_records)} voting records found")
                if processed_content.detailed_summary:
                    improvements.append("Detailed summary with formatting")
                if processed_content.vote_statistics:
                    improvements.append(f"Vote statistics: {processed_content.vote_statistics}")

                if improvements:
                    print(f"   ✨ Improvements: {', '.join(improvements)}")

                if not dry_run:
                    # Update the meeting record
                    meeting.summary = processed_content.summary
                    meeting.detailed_summary = processed_content.detailed_summary
                    meeting.voting_records = [vote.dict() for vote in processed_content.voting_records]
                    meeting.vote_statistics = processed_content.vote_statistics

                    # Update categories and keywords (as JSON for now)
                    if hasattr(meeting, 'ai_categories'):
                        meeting.ai_categories = processed_content.categories
                    if hasattr(meeting, 'ai_keywords'):
                        meeting.ai_keywords = processed_content.keywords

                    db.commit()
                    print(f"   ✅ Updated in database")
                    updated_count += 1
                else:
                    print(f"   🔍 Would update (dry run)")

                print()

            except Exception as e:
                print(f"   ❌ Error processing: {str(e)}")
                error_count += 1
                continue

        # Summary
        print("📊 Update Summary:")
        print(f"   Meetings processed: {len(meetings)}")
        if not dry_run:
            print(f"   Successfully updated: {updated_count}")
        print(f"   Errors encountered: {error_count}")

        if dry_run:
            print("\n🔍 This was a dry run. Use --apply to make changes.")
        else:
            print(f"\n✅ Enhanced AI processing complete! Updated {updated_count} meetings.")

        print("\n🎯 Benefits of Enhanced Processing:")
        print("   • Cleaner, more focused summaries")
        print("   • Reduced keyword noise (5-8 vs 10-15)")
        print("   • Structured detailed summaries with bullet points")
        print("   • Voting record extraction with member names")
        print("   • Better categorization accuracy")
        print("   • GPT-4 processing for higher quality")

    except Exception as e:
        logger.error(f"Error updating AI summaries: {str(e)}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update meetings with enhanced AI summaries")
    parser.add_argument("--limit", type=int, default=10, help="Number of meetings to process (default: 10)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")

    args = parser.parse_args()

    update_ai_summaries(limit=args.limit, dry_run=not args.apply)
