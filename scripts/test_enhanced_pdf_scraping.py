#!/usr/bin/env python3
"""
Test script for enhanced PDF scraping with embedded minutes extraction
"""

import sys
from pathlib import Path
import asyncio

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.scrapers.tgov_scraper import TGOVScraper
from app.core.database import SessionLocal

async def test_enhanced_pdf_scraping():
    print("🧪 Testing Enhanced PDF Scraping with Embedded Minutes Extraction")
    print("=" * 70)

    db = SessionLocal()
    try:
        scraper = TGOVScraper(db)

        # Test 1: PDF Text Extraction
        print("\n📄 Test 1: PDF Text Extraction")

        # Use an existing PDF file for testing
        pdf_storage = Path("backend/storage/pdfs")
        test_pdfs = list(pdf_storage.glob("*.pdf"))[:3]  # Test first 3 PDFs

        if not test_pdfs:
            print("❌ No PDF files found in storage for testing")
            return

        for pdf_file in test_pdfs:
            print(f"\nTesting PDF: {pdf_file.name}")

            # Extract text
            text_content = scraper.extract_text_from_pdf(pdf_file)

            if text_content:
                text_length = len(text_content)
                print(f"  ✅ Extracted {text_length} characters of text")

                # Show first 200 characters as sample
                sample_text = text_content.strip()[:200].replace('\n', ' ')
                print(f"  📝 Sample: {sample_text}...")

                # Test 2: Find embedded links
                print(f"\n  🔍 Searching for embedded minutes links...")
                minutes_links = scraper.find_meeting_minutes_links_in_pdf_text(text_content)

                if minutes_links:
                    print(f"  ✅ Found {len(minutes_links)} potential minutes links:")
                    for i, link in enumerate(minutes_links):
                        print(f"    {i+1}. {link}")
                else:
                    print("  ⚠️ No minutes links found in this PDF")

            else:
                print("  ❌ Failed to extract text from PDF")

        # Test 3: URL Pattern Recognition
        print(f"\n🔗 Test 3: URL Pattern Recognition")

        # Test with sample agenda text containing various link patterns
        sample_agenda_text = """
        TULSA CITY COUNCIL AGENDA
        Regular Meeting - January 15, 2024

        Meeting Minutes will be available at:
        https://www.cityoftulsa.org/media/115141/01152024-minutes.pdf

        Previous meeting minutes: 24-123-1Minutes.pdf

        Transcript available: https://tulsa-ok.granicus.com/transcript?meeting=24-456

        Additional documents:
        - Budget report: cityoftulsa.org/documents/budget-2024.pdf
        - Minutes from 01/08/2024: Minutes_24_01_08.pdf
        """

        print("Testing sample agenda text...")
        found_links = scraper.find_meeting_minutes_links_in_pdf_text(sample_agenda_text)

        print(f"✅ Found {len(found_links)} links in sample text:")
        for i, link in enumerate(found_links):
            print(f"  {i+1}. {link}")

        # Test 4: Complete workflow simulation
        print(f"\n🚀 Test 4: Complete Workflow Simulation")

        if test_pdfs:
            test_pdf = test_pdfs[0]
            test_meeting_id = "test-enhanced-workflow"

            print(f"Simulating complete workflow with: {test_pdf.name}")

            # Simulate the complete minutes extraction workflow
            downloaded_minutes = scraper.download_meeting_minutes_from_agenda(
                test_pdf,
                test_meeting_id
            )

            print(f"✅ Workflow completed. Downloaded {len(downloaded_minutes)} minutes files:")
            for minutes_file in downloaded_minutes:
                print(f"  - {minutes_file}")

        print(f"\n🎉 Enhanced PDF Scraping Test Complete!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_enhanced_pdf_scraping())
