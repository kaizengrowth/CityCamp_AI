#!/usr/bin/env python3
"""
Test script for the Tulsa Archive scraper
"""

import sys
from pathlib import Path
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.scrapers.tulsa_archive_scraper import TulsaArchiveScraper
from app.core.database import SessionLocal

async def test_tulsa_archive_scraper():
    print("🧪 Testing Tulsa Archive Scraper")
    print("=" * 60)

    db = SessionLocal()
    try:
        scraper = TulsaArchiveScraper(db)

        # Test 1: Basic scraping capability
        print("\n📋 Test 1: Archive Page Scraping")
        print("-" * 40)

        meetings_data = scraper.scrape_archive_meetings()

        if meetings_data:
            print(f"✅ Found {len(meetings_data)} meetings in archive")

            # Show sample meetings
            print("\n📋 Sample meetings found:")
            for i, meeting in enumerate(meetings_data[:5]):  # Show first 5
                print(f"  {i+1}. {meeting['title']}")
                print(f"     Type: {meeting['meeting_type']} | Doc: {meeting['document_type']}")
                print(f"     Date: {meeting['meeting_date']}")
                print(f"     URL: {meeting['agenda_url'][:60]}...")
                print()
        else:
            print("❌ No meetings found - check scraper logic or website structure")
            return

        # Test 2: Document categorization
        print("\n🏷️ Test 2: Document Categorization")
        print("-" * 40)

        test_types = [
            "Regular",
            "Urban And Economic Development Committee",
            "Public Works Committee",
            "Budget and Special Projects Committee Meeting"
        ]

        for test_type in test_types:
            doc_type, meeting_cat = scraper.categorize_meeting_type(test_type)
            print(f"  '{test_type}' → Document: {doc_type}, Category: {meeting_cat}")

        # Test 3: URL parsing and external ID extraction
        print("\n🔗 Test 3: URL Parsing")
        print("-" * 40)

        test_urls = [
            "https://www.cityoftulsa.org/apps/COTDisplayDocument/?DocumentType=Agenda&DocumentIdentifiers=29981",
            "https://www.cityoftulsa.org/apps/COTDisplayDocument/?DocumentType=Minutes&DocumentIdentifiers=12345"
        ]

        for url in test_urls:
            external_id = scraper._extract_external_id_from_url(url)
            print(f"  URL: {url}")
            print(f"  External ID: {external_id}")
            print()

        # Test 4: Date parsing
        print("\n📅 Test 4: Date Parsing")
        print("-" * 40)

        test_dates = [
            "8/6/2025 10:30 AM",
            "12/15/2024 2:30 PM",
            "1/1/2024 9:00 AM"
        ]

        for date_str in test_dates:
            parsed_date = scraper._parse_meeting_date(date_str)
            if parsed_date:
                print(f"  '{date_str}' → {parsed_date.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"  '{date_str}' → Failed to parse")

        # Test 5: PDF text extraction (if we have any PDFs)
        print("\n📄 Test 5: PDF Text Extraction")
        print("-" * 40)

        pdf_storage = Path("backend/storage/pdfs")
        test_pdfs = list(pdf_storage.glob("*.pdf"))[:2]  # Test first 2 PDFs

        if test_pdfs:
            for pdf_file in test_pdfs:
                print(f"\nTesting PDF: {pdf_file.name}")

                text_content = scraper.extract_text_from_pdf(pdf_file)
                if text_content:
                    text_length = len(text_content)
                    print(f"  ✅ Extracted {text_length} characters")

                    # Test embedded links detection
                    embedded_links = scraper.find_embedded_minutes_links(text_content)
                    print(f"  🔍 Found {len(embedded_links)} potential minutes links")

                    for link in embedded_links[:3]:  # Show first 3 links
                        print(f"    - {link}")
                else:
                    print("  ❌ Failed to extract text")
        else:
            print("  ⚠️ No PDF files found for testing")

        # Test 6: Limited scraping run
        print("\n🚀 Test 6: Limited Scraping Run")
        print("-" * 40)

        print("Running limited scrape (first 3 meetings)...")
        stats = await scraper.scrape_and_download_all(max_meetings=3)

        print(f"\n📊 Scraping Results:")
        print(f"  - Meetings found: {stats['meetings_found']}")
        print(f"  - Documents downloaded: {stats['documents_downloaded']}")
        print(f"  - Minutes extracted: {stats['minutes_extracted']}")
        print(f"  - Errors: {stats['errors']}")

        # Test 7: Database integration check
        print("\n💾 Test 7: Database Integration")
        print("-" * 40)

        # Check if any meetings were created
        from app.models.meeting import Meeting
        tulsa_archive_meetings = db.query(Meeting).filter(
            Meeting.source == 'tulsa_archive'
        ).count()

        print(f"  Tulsa Archive meetings in database: {tulsa_archive_meetings}")

        if tulsa_archive_meetings > 0:
            # Show sample meeting
            sample_meeting = db.query(Meeting).filter(
                Meeting.source == 'tulsa_archive'
            ).first()

            print(f"  Sample meeting:")
            print(f"    - Title: {sample_meeting.title}")
            print(f"    - Type: {sample_meeting.meeting_type}")
            print(f"    - Document Type: {getattr(sample_meeting, 'document_type', 'Not set')}")
            print(f"    - Date: {sample_meeting.meeting_date}")

        print(f"\n🎉 Tulsa Archive Scraper Test Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Check for command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test Tulsa Archive Scraper')
    parser.add_argument('--aws-db-url', help='AWS RDS database URL for testing')
    args = parser.parse_args()

    if args.aws_db_url:
        print(f"🔗 Testing against AWS database...")
        # Use custom database URL by temporarily overriding the DATABASE_URL
        import os
        os.environ['DATABASE_URL'] = args.aws_db_url

    asyncio.run(test_tulsa_archive_scraper())
