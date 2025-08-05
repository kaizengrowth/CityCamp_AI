#!/usr/bin/env python3
"""
Test Enhanced AI Processing
Test the improved AI categorization service on existing meetings
"""

import asyncio
import os
import sys
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


def test_enhanced_ai_processing():
    """Test enhanced AI processing on a few existing meetings"""

    print("🤖 Testing Enhanced AI Processing")
    print("=" * 50)

    db = SessionLocal()
    ai_service = AICategorization()

    try:
        # Get a few recent meetings to test
        recent_meetings = (
            db.query(Meeting)
            .filter(Meeting.minutes_url.isnot(None))
            .order_by(Meeting.meeting_date.desc())
            .limit(3)
            .all()
        )

        if not recent_meetings:
            print("❌ No meetings with PDFs found for testing")
            return

        print(f"📋 Testing {len(recent_meetings)} meetings...")
        print()

        for i, meeting in enumerate(recent_meetings, 1):
            print(f"🔍 Meeting {i}: {meeting.title}")
            print(f"   Date: {meeting.meeting_date}")
            print(f"   PDF: {meeting.minutes_url}")

            try:
                # Construct full PDF path
                pdf_path = Path("backend") / meeting.minutes_url
                if not pdf_path.exists():
                    print(f"   ❌ PDF file not found: {pdf_path}")
                    continue

                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()

                # Process with enhanced AI
                print("   🤖 Processing with enhanced AI...")
                processed_content = ai_service.process_meeting_minutes(
                    pdf_content, meeting.id, db
                )

                # Display results
                print(f"   📊 Results:")
                print(f"      Categories: {len(processed_content.categories)}")
                print(f"      Keywords: {len(processed_content.keywords)}")
                print(f"      Voting Records: {len(processed_content.voting_records)}")

                print(f"   📝 Summary (Old): {meeting.summary[:100] if meeting.summary else 'None'}...")
                print(f"   📝 Summary (New): {processed_content.summary[:100]}...")

                if processed_content.detailed_summary:
                    print(f"   📋 Detailed Summary Preview:")
                    lines = processed_content.detailed_summary.split('\n')[:3]
                    for line in lines:
                        if line.strip():
                            print(f"      {line.strip()[:80]}...")

                if processed_content.voting_records:
                    print(f"   🗳️  Voting Records Found:")
                    for vote in processed_content.voting_records[:2]:
                        print(f"      {vote.council_member}: {vote.vote} on '{vote.agenda_item[:50]}...'")

                if processed_content.vote_statistics:
                    print(f"   📈 Vote Statistics: {processed_content.vote_statistics}")

                print()

            except Exception as e:
                print(f"   ❌ Error processing meeting: {str(e)}")
                continue

        print("✅ Enhanced AI processing test completed!")
        print("\n🎯 Key Improvements:")
        print("   • Cleaner, more structured summaries")
        print("   • Better keyword extraction (5-8 focused terms)")
        print("   • Detailed summaries with bullet points")
        print("   • Voting record extraction")
        print("   • Enhanced statistics tracking")
        print("   • Upgraded to GPT-4 for better accuracy")

    except Exception as e:
        logger.error(f"Error in AI processing test: {str(e)}")

    finally:
        db.close()


if __name__ == "__main__":
    test_enhanced_ai_processing()
