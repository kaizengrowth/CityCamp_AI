#!/usr/bin/env python3
"""
Comprehensive Tulsa Archive Scraper - Production Script
Scrapes ALL historical documents (2020-2025) from cityoftulsa.org/apps/TulsaCouncilArchive
"""

import sys
from pathlib import Path
import asyncio
import argparse

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Load environment variables from backend/.env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

from app.scrapers.tulsa_archive_scraper import TulsaArchiveScraper
from app.core.database import SessionLocal
from app.services.ai_categorization_service import AICategorization
from app.models.meeting import Meeting

async def run_comprehensive_scraper(
    start_year: int = 2020,
    end_year: int = 2025,
    meeting_types: list = None,
    max_downloads: int = 0,
    process_ai: bool = False,
    aws_db_url: str = None,
    dry_run: bool = False
):
    """
    Run comprehensive historical scraping of Tulsa Archive
    """

    print("🚀 COMPREHENSIVE TULSA ARCHIVE SCRAPER")
    print("=" * 60)
    print(f"📅 Date Range: {start_year} - {end_year}")
    print(f"🏷️ Meeting Types: {'All' if not meeting_types else f'{len(meeting_types)} selected'}")
    print(f"💾 Database: {'AWS RDS' if aws_db_url else 'Local'}")
    print(f"🤖 AI Processing: {'Enabled' if process_ai else 'Disabled'}")
    print(f"🧪 Dry Run: {'Yes' if dry_run else 'No'}")
    print("=" * 60)

    # Database setup
    if aws_db_url:
        import os
        os.environ['DATABASE_URL'] = aws_db_url
        print("🔗 Using AWS RDS database")
    else:
        print("🔗 Using local database configuration")

    db = SessionLocal()

    try:
        scraper = TulsaArchiveScraper(db)

        # Phase 1: Comprehensive scraping
        print(f"\n📡 PHASE 1: COMPREHENSIVE SCRAPING")
        print("-" * 50)

        if dry_run:
            print("🧪 DRY RUN: Would scrape historical data but not saving")
            # Just test with 2024 data for dry run
            start_year = 2024
            end_year = 2024
            meeting_types = ['Regular']  # Just test with Regular meetings

        meetings_data = scraper.scrape_comprehensive_archive(
            start_year=start_year,
            end_year=end_year,
            meeting_types=meeting_types
        )

        print(f"\n📊 SCRAPING RESULTS:")
        print(f"  Total meetings found: {len(meetings_data)}")

        # Breakdown by meeting type
        type_counts = {}
        for meeting in meetings_data:
            meeting_type = meeting['meeting_type']
            type_counts[meeting_type] = type_counts.get(meeting_type, 0) + 1

        print(f"\n📋 Breakdown by meeting type:")
        for meeting_type, count in sorted(type_counts.items()):
            print(f"  • {meeting_type}: {count} meetings")

        if dry_run:
            print(f"\n🧪 DRY RUN COMPLETE - No data saved")
            return

        # Phase 2: Document download and database storage
        print(f"\n📥 PHASE 2: DOCUMENT DOWNLOAD & DATABASE STORAGE")
        print("-" * 50)

        download_count = 0
        created_count = 0
        updated_count = 0
        error_count = 0

        # Limit downloads if specified
        meetings_to_process = meetings_data
        if max_downloads > 0:
            meetings_to_process = meetings_data[:max_downloads]
            print(f"⚠️ Limiting to first {max_downloads} meetings")

        for i, meeting_data in enumerate(meetings_to_process):
            try:
                print(f"\n📋 Processing {i+1}/{len(meetings_to_process)}: {meeting_data['title']}")

                # Check if meeting already exists
                existing_meeting = db.query(Meeting).filter(
                    Meeting.external_id == meeting_data['external_id']
                ).first()

                is_update = existing_meeting is not None

                # Download document
                pdf_path = scraper.download_document(
                    meeting_data['agenda_url'],
                    meeting_data['external_id'],
                    meeting_data['document_type']
                )

                if pdf_path:
                    download_count += 1
                    print(f"  ✅ Downloaded: {pdf_path}")

                    # Create/update meeting record
                    meeting = scraper.create_or_update_meeting(meeting_data, pdf_path)

                    if meeting:
                        if is_update:
                            updated_count += 1
                            print(f"  🔄 Updated existing meeting")
                        else:
                            created_count += 1
                            print(f"  ➕ Created new meeting")

                        # Process Regular meetings for embedded minutes
                        if meeting_data['meeting_type'] == 'regular_council':
                            full_pdf_path = Path("backend") / pdf_path
                            if full_pdf_path.exists():
                                print(f"  🔍 Searching for embedded minutes...")
                                embedded_minutes = scraper.process_regular_meeting_agenda(
                                    meeting_data,
                                    full_pdf_path
                                )

                                if embedded_minutes:
                                    print(f"  📝 Downloaded {len(embedded_minutes)} embedded minutes")
                    else:
                        error_count += 1
                        print(f"  ❌ Failed to create/update meeting record")
                else:
                    error_count += 1
                    print(f"  ❌ Failed to download document")

            except Exception as e:
                error_count += 1
                print(f"  ❌ Error processing meeting: {str(e)}")
                continue

        # Summary of Phase 2
        print(f"\n📊 DOWNLOAD & STORAGE RESULTS:")
        print(f"  Documents downloaded: {download_count}")
        print(f"  Meetings created: {created_count}")
        print(f"  Meetings updated: {updated_count}")
        print(f"  Errors: {error_count}")

        # Phase 3: AI Processing (if enabled)
        if process_ai:
            print(f"\n🤖 PHASE 3: AI PROCESSING")
            print("-" * 50)

            try:
                ai_service = AICategorization()
                ai_service.initialize_categories_in_db(db)

                # Find meetings that need AI processing
                unprocessed_meetings = db.query(Meeting).filter(
                    Meeting.source == 'tulsa_archive',
                    Meeting.minutes_url.isnot(None),
                    Meeting.summary.is_(None)
                ).all()

                print(f"Found {len(unprocessed_meetings)} meetings needing AI processing")

                ai_processed = 0
                for meeting in unprocessed_meetings:
                    try:
                        print(f"  🤖 Processing: {meeting.title}")

                        # Read PDF content
                        pdf_path = Path("backend") / meeting.minutes_url
                        if pdf_path.exists():
                            text_content = scraper.extract_text_from_pdf(pdf_path)

                            if text_content:
                                # Process with AI
                                processed_content = ai_service.categorize_content_with_ai(text_content)

                                # Update meeting with AI results
                                meeting.topics = processed_content.categories
                                meeting.keywords = processed_content.keywords
                                meeting.summary = processed_content.summary
                                meeting.detailed_summary = processed_content.detailed_summary
                                meeting.voting_records = [vote.__dict__ for vote in processed_content.voting_records]
                                meeting.vote_statistics = processed_content.vote_statistics

                                db.commit()
                                ai_processed += 1
                                print(f"    ✅ AI processing complete")
                            else:
                                print(f"    ⚠️ No text content extracted")
                        else:
                            print(f"    ⚠️ PDF file not found: {meeting.minutes_url}")

                    except Exception as e:
                        print(f"    ❌ AI processing failed: {str(e)}")
                        continue

                print(f"\n📊 AI PROCESSING RESULTS:")
                print(f"  Meetings processed: {ai_processed}")

            except Exception as e:
                print(f"❌ AI processing setup failed: {str(e)}")

        # Final summary
        print(f"\n🎉 COMPREHENSIVE SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"📊 FINAL RESULTS:")
        print(f"  • Historical range: {start_year} - {end_year}")
        print(f"  • Meeting types scraped: {len(type_counts)}")
        print(f"  • Total meetings found: {len(meetings_data)}")
        print(f"  • Documents downloaded: {download_count}")
        print(f"  • Database records created: {created_count}")
        print(f"  • Database records updated: {updated_count}")
        if process_ai:
            print(f"  • AI processing completed: {ai_processed if 'ai_processed' in locals() else 0}")
        print(f"  • Errors encountered: {error_count}")
        print("=" * 60)

        if error_count == 0:
            print("🏆 Perfect run - no errors!")
        elif error_count < len(meetings_data) * 0.1:
            print("✅ Excellent run - minimal errors")
        else:
            print("⚠️ Some errors encountered - check logs above")

        print(f"\n🌐 Ready for frontend access with comprehensive filtering!")

    except Exception as e:
        print(f"❌ Fatal error in comprehensive scraper: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Comprehensive Tulsa Archive Scraper')

    # Date range options
    parser.add_argument('--start-year', type=int, default=2020,
                       help='Start year for scraping (default: 2020)')
    parser.add_argument('--end-year', type=int, default=2025,
                       help='End year for scraping (default: 2025)')

    # Meeting type filtering
    parser.add_argument('--meeting-types', nargs='+',
                       help='Specific meeting types to scrape (default: all)')

    # Limits and options
    parser.add_argument('--max-downloads', type=int, default=0,
                       help='Maximum number of documents to download (0 = no limit)')
    parser.add_argument('--process-ai', action='store_true',
                       help='Enable AI processing of downloaded documents')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test run without saving data')

    # Database options
    parser.add_argument('--aws-db-url',
                       help='AWS RDS database URL')

    args = parser.parse_args()

    # Run the comprehensive scraper
    asyncio.run(run_comprehensive_scraper(
        start_year=args.start_year,
        end_year=args.end_year,
        meeting_types=args.meeting_types,
        max_downloads=args.max_downloads,
        process_ai=args.process_ai,
        aws_db_url=args.aws_db_url,
        dry_run=args.dry_run
    ))

if __name__ == "__main__":
    main()
