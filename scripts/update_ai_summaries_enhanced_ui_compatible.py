#!/usr/bin/env python3
"""
Enhanced AI Summaries Update Script - UI COMPATIBLE VERSION
Processes meetings with enhanced AI and formats data correctly for the new UI components
"""

import os
import sys
import argparse
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.meeting import Meeting
from app.services.ai_categorization_service import AICategorization
from app.services.voting_statistics_formatter import VotingStatisticsFormatter
import logging

# Setup logging with file output
import datetime
import json
log_filename = f"logs/ai_processing_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)


def standardize_meeting_title(original_title: str, meeting_date) -> str:
    """Create standardized meeting title following convention"""

    # Check for special meeting indicators
    if any(keyword in original_title.lower() for keyword in ["special", "emergency", "workshop"]):
        return "Special Meeting"

    # Check for committee meetings
    if any(keyword in original_title.lower() for keyword in ["committee", "planning", "budget", "finance"]):
        return "Committee Meeting"

    # Check for work sessions
    if any(keyword in original_title.lower() for keyword in ["work session", "worksession", "study session"]):
        return "Work Session"

    # Check for public hearings
    if any(keyword in original_title.lower() for keyword in ["public hearing", "hearing"]):
        return "Public Hearing"

    # Default to regular meeting for standard council meetings
    return "Regular Meeting"


def update_ai_summaries_enhanced_ui_compatible(limit: int = 10, dry_run: bool = True):
    """Update meetings with enhanced AI processing and UI-compatible data formatting"""

    print("🚀 Enhanced AI Processing with Beautiful UI Components")
    print("=" * 80)
    print("🎯 Enhanced Features:")
    print("   • Comprehensive voting records with member names and vote counts")
    print("   • Beautiful voting breakdown UI with color-coded statistics")
    print("   • Individual voting records with detailed member votes")
    print("   • Council attendance tracking (present/absent)")
    print("   • UI-compatible data formatting")
    print("   • Standardized meeting titles")
    print()

    db = SessionLocal()
    ai_service = AICategorization()

    try:
        # Get meetings that have PDFs, ordered by date (newest first)
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

        logger.info(f"Starting AI processing session: {len(meetings)} meetings, mode: {'LIVE' if not dry_run else 'DRY_RUN'}")
        print(f"📋 Processing {len(meetings)} meetings...")
        print(f"🔍 Mode: {'DRY RUN' if dry_run else 'LIVE UPDATE'}")
        print()

        updated_count = 0
        error_count = 0

        for i, meeting in enumerate(meetings, 1):
            logger.info(f"Processing meeting {i}/{len(meetings)}: ID={meeting.id}, Title='{meeting.title}'")
            print(f"🔍 [{i}/{len(meetings)}] {meeting.title}")
            print(f"   📅 Date: {meeting.meeting_date}")
            print(f"   📄 PDF: {meeting.minutes_url}")
            print(f"   🆔 ID: {meeting.id}")

            try:
                # Handle both local paths and GitHub URLs
                if meeting.minutes_url.startswith('http'):
                    # It's a GitHub URL, find the local file
                    filename = meeting.minutes_url.split('/')[-1]
                    from urllib.parse import unquote
                    filename = unquote(filename)

                    # Check in both new and old directories
                    pdf_path = None
                    for test_path in [
                        Path("tests/new_downloaded_documents") / filename,
                        Path("tests/downloaded_documents") / filename,
                        Path("backend/tests/new_downloaded_documents") / filename,
                        Path("backend/tests/downloaded_documents") / filename
                    ]:
                        if test_path.exists():
                            pdf_path = test_path
                            break
                else:
                    # It's a local path
                    pdf_path = Path("backend") / meeting.minutes_url

                if not pdf_path or not pdf_path.exists():
                    print(f"   ⚠️  PDF file not found: {pdf_path}")
                    error_count += 1
                    continue

                print(f"   📁 Found PDF: {pdf_path}")

                # Read PDF content
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()

                # Process with enhanced AI
                print("   🤖 Processing with Enhanced AI (GPT-4)...")
                start_time = datetime.datetime.now()

                # Extract PDF filename for image matching
                pdf_filename = None
                if meeting.minutes_url.startswith('http'):
                    pdf_filename = meeting.minutes_url.split('/')[-1]
                    from urllib.parse import unquote
                    pdf_filename = unquote(pdf_filename)
                else:
                    pdf_filename = Path(meeting.minutes_url).name

                processed_content = ai_service.process_meeting_minutes(
                    pdf_content, meeting.id, db, meeting.title, pdf_filename
                )
                processing_time = (datetime.datetime.now() - start_time).total_seconds()

                # Format data for UI compatibility using proper formatter
                formatter = VotingStatisticsFormatter()
                formatted_voting_records = formatter.format_voting_records_for_ui(
                    processed_content.voting_records
                )
                formatted_vote_statistics = formatter.format_vote_statistics_for_ui(
                    processed_content.vote_statistics
                )

                # Show detailed results
                print(f"   ✨ Enhanced Results:")
                print(f"      📊 Categories: {len(processed_content.categories)}")
                print(f"      🏷️  Keywords: {len(processed_content.keywords)} (focused)")
                print(f"      📝 Summary: {len(processed_content.summary)} chars")
                print(f"      📋 Detailed Summary: {'✅' if processed_content.detailed_summary else '❌'}")
                print(f"      🗳️  Voting Records: {len(formatted_voting_records)} items")
                print(f"      🖼️  Images: {len(processed_content.image_paths)} pages")

                # Show vote statistics
                if formatted_vote_statistics:
                    print(f"      📈 Vote Statistics:")
                    print(f"         • Agenda Items: {formatted_vote_statistics.get('total_agenda_items', 'N/A')}")
                    print(f"         • Votes Taken: {formatted_vote_statistics.get('total_votes', 'N/A')}")
                    print(f"         • Items Passed: {formatted_vote_statistics.get('items_passed', 'N/A')}")
                    print(f"         • Unanimous: {formatted_vote_statistics.get('unanimous_votes', 'N/A')}")
                    print(f"         • Members Present: {len(formatted_vote_statistics.get('council_members_present', []))}")

                if not dry_run:
                    # Create standardized title
                    standardized_title = standardize_meeting_title(meeting.title, meeting.meeting_date)

                    # Update meeting with UI-compatible data
                    meeting.title = standardized_title
                    meeting.summary = processed_content.summary
                    meeting.detailed_summary = processed_content.detailed_summary
                    meeting.voting_records = formatted_voting_records  # UI-compatible format
                    meeting.vote_statistics = formatted_vote_statistics  # UI-compatible format
                    meeting.image_paths = processed_content.image_paths  # PDF page images

                    # Save topics and keywords
                    meeting.topics = processed_content.categories
                    meeting.keywords = processed_content.keywords

                    # Commit to database
                    db.commit()
                    print(f"   ✅ Updated in database with UI-compatible data")
                    updated_count += 1
                else:
                    print(f"   🔍 Would update with enhanced UI-compatible data (dry run)")

                print()

            except Exception as e:
                print(f"   ❌ Error processing: {str(e)}")
                logger.error(f"Error processing meeting {meeting.id}: {e}", exc_info=True)
                error_count += 1
                continue

        # Final Summary
        print("📊 Enhanced Processing Summary:")
        print(f"   Meetings processed: {len(meetings)}")
        if not dry_run:
            print(f"   Successfully updated: {updated_count}")
        print(f"   Errors encountered: {error_count}")

        if dry_run:
            print("\n🔍 This was a dry run. Use --apply to make changes.")
        else:
            print(f"\n✅ Enhanced AI processing complete! Updated {updated_count} meetings.")

        print("\n🎯 Beautiful UI Features Ready:")
        print("   • 📊 Enhanced Meeting Statistics with color-coded cards")
        print("   • 🗳️  Voting Breakdown with pass/fail/tabled counts")
        print("   • 👥 Council Attendance tracking (present/absent members)")
        print("   • 🗳️  Individual Voting Records with member-by-member votes")
        print("   • 🎨 Color-coded vote results (green=passed, red=failed, yellow=tabled)")
        print("   • 🖼️  Image Carousel for viewing meeting document pages")
        print("   • 📱 Responsive grid layout for all screen sizes")

    except Exception as e:
        print(f"❌ Error during enhanced processing: {e}")
        logger.error(f"Fatal error during processing: {e}", exc_info=True)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Enhanced AI processing with beautiful UI components")
    parser.add_argument("--limit", type=int, default=26, help="Number of meetings to process (default: 26)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")

    args = parser.parse_args()

    update_ai_summaries_enhanced_ui_compatible(
        limit=args.limit,
        dry_run=not args.apply
    )

if __name__ == "__main__":
    main()
