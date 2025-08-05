#!/usr/bin/env python3
"""
Run live scraper to fetch new meetings from Tulsa City Council website
and automatically process downloaded PDFs with AI
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
import sys

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.scrapers.meeting_scraper import MeetingScraper
from app.services.ai_categorization_service import AICategorization
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def main():
    parser = argparse.ArgumentParser(description="Run live meeting scraper with AI processing")
    parser.add_argument("--aws-db-url", help="AWS RDS database URL")
    parser.add_argument("--days-ahead", type=int, default=30, help="Days ahead to scrape (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Test connection without saving")
    parser.add_argument("--process-ai", action="store_true", default=True, help="Process downloaded PDFs with AI (default: True)")

    args = parser.parse_args()

    print(f"🕸️ Starting enhanced live scraper for next {args.days_ahead} days...")
    print(f"📅 Scrape date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 AI processing: {'Enabled' if args.process_ai else 'Disabled'}")

    if args.dry_run:
        print("🧪 DRY RUN MODE - No data will be saved")

    # Setup database connection
    if args.aws_db_url:
        print("📡 Connecting to AWS RDS database...")
        engine = create_engine(args.aws_db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    else:
        print("🏠 Using local database...")
        from app.core.database import SessionLocal

    async def run_enhanced_scraper():
        db = SessionLocal()
        try:
            scraper = MeetingScraper(db)

            print("🌐 Connecting to Tulsa City Council Granicus system...")
            print("🔗 URL: https://tulsa-ok.granicus.com/ViewPublisher.php?view_id=4")

            if not args.dry_run:
                # Step 1: Run live scraping (now with PDF downloads)
                stats = await scraper.run_full_scrape(days_ahead=args.days_ahead)

                print(f"\n📊 Live Scraping Results:")
                print(f"  ✅ Meetings found: {stats.get('meetings_found', 0)}")
                print(f"  🔄 Meetings updated: {stats.get('meetings_updated', 0)}")
                print(f"  📋 Agenda items created: {stats.get('agenda_items_created', 0)}")
                print(f"  📬 Notifications sent: {stats.get('notifications_sent', 0)}")

                # Step 2: Process downloaded PDFs with AI
                if args.process_ai and stats.get('meetings_found', 0) > 0:
                    print(f"\n🤖 Processing newly downloaded PDFs with AI...")

                    try:
                        ai_service = AICategorization()
                        ai_service.initialize_categories_in_db(db)

                        # Find meetings that have local PDF files but no AI processing
                        from app.models.meeting import Meeting
                        unprocessed_meetings = db.query(Meeting).filter(
                            Meeting.source == 'tgov_scraper',
                            Meeting.minutes_url.isnot(None),
                            Meeting.minutes_url.like('storage/pdfs/%'),
                            Meeting.summary.is_(None)  # Not yet processed by AI
                        ).all()

                        print(f"📋 Found {len(unprocessed_meetings)} meetings with new PDFs to process")

                        for meeting in unprocessed_meetings:
                            try:
                                pdf_path = Path("backend") / meeting.minutes_url
                                if pdf_path.exists():
                                    print(f"  🔄 Processing {meeting.external_id}...")

                                    # Extract text and run AI analysis
                                    import pdfplumber
                                    text_content = ""
                                    with pdfplumber.open(pdf_path) as pdf:
                                        for page in pdf.pages:
                                            page_text = page.extract_text()
                                            if page_text:
                                                text_content += page_text + "\n"

                                    if text_content.strip():
                                        # Run AI categorization
                                        processed_content = ai_service.categorize_content_with_ai(
                                            text_content, meeting.title
                                        )

                                        # Update meeting with AI results
                                        meeting.topics = processed_content.categories
                                        meeting.keywords = processed_content.keywords
                                        meeting.summary = processed_content.summary
                                        meeting.detailed_summary = processed_content.detailed_summary
                                        meeting.voting_records = [vote.__dict__ for vote in processed_content.voting_records]
                                        meeting.vote_statistics = processed_content.vote_statistics

                                        db.commit()

                                        print(f"    ✅ AI processed: {len(processed_content.categories)} categories, {len(processed_content.keywords)} keywords")
                                    else:
                                        print(f"    ⚠️ No text content extracted from PDF")
                                else:
                                    print(f"    ❌ PDF file not found: {pdf_path}")

                            except Exception as e:
                                print(f"    ❌ Error processing {meeting.external_id}: {str(e)}")
                                continue

                        print(f"🎉 AI processing completed!")

                    except Exception as e:
                        print(f"❌ AI processing error: {str(e)}")

                if stats.get('meetings_found', 0) > 0:
                    print("\n🎉 New meetings successfully scraped and processed!")
                    print("📁 PDFs downloaded to backend/storage/pdfs/")
                    print("🤖 AI analysis completed for new content")
                else:
                    print("\n✅ Scraping completed - no new meetings found")
                    print("📅 This is normal if no upcoming meetings are scheduled")

            else:
                print("🧪 Dry run - connection test only")

        except Exception as e:
            print(f"❌ Scraper error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()

    # Run the enhanced scraper
    asyncio.run(run_enhanced_scraper())
    print("\n✅ Enhanced live scraping completed!")

if __name__ == "__main__":
    main()
