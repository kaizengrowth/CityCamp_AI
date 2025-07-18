#!/usr/bin/env python3
"""
Local test script for the CityCamp AI scraper
Run this to test scraper functionality without the full API
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.scrapers.tgov_scraper import TGOVScraper
from app.scrapers.meeting_scraper import MeetingScraper
from app.models.meeting import Meeting, AgendaItem
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test_scraper.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

async def test_tgov_scraper():
    """Test the TGOV scraper directly"""
    print("\n" + "="*50)
    print("TESTING TGOV SCRAPER")
    print("="*50)

    db = SessionLocal()
    try:
        scraper = TGOVScraper(db)

        print("1. Testing upcoming meetings scrape...")
        meetings = await scraper.scrape_upcoming_meetings(days_ahead=30)
        print(f"   Found {len(meetings)} meetings")

        for meeting in meetings:
            print(f"   - {meeting.title} on {meeting.meeting_date}")

            # Test agenda items scraping
            print(f"     Testing agenda items for: {meeting.title}")
            agenda_items = await scraper.scrape_agenda_items(meeting)
            print(f"     Found {len(agenda_items)} agenda items")

            # Test minutes scraping if it's a past meeting
            if meeting.meeting_date.date() < asyncio.get_event_loop().time():
                print(f"     Testing minutes for: {meeting.title}")
                minutes = await scraper.scrape_meeting_minutes(meeting)
                if minutes:
                    print(f"     Minutes found: {len(minutes)} characters")
                    print(f"     Preview: {minutes[:200]}...")
                else:
                    print("     No minutes found")
            else:
                print("     Meeting is in the future, skipping minutes")

    except Exception as e:
        print(f"Error testing TGOV scraper: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

async def test_meeting_scraper():
    """Test the full meeting scraper workflow"""
    print("\n" + "="*50)
    print("TESTING MEETING SCRAPER WORKFLOW")
    print("="*50)

    db = SessionLocal()
    try:
        scraper = MeetingScraper(db)

        print("Running full scrape cycle...")
        stats = await scraper.run_full_scrape(days_ahead=30)

        print("Scrape Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Show what's in the database
        meetings = db.query(Meeting).all()
        print(f"\nTotal meetings in database: {len(meetings)}")

        for meeting in meetings:
            print(f"- {meeting.title}")
            print(f"  Date: {meeting.meeting_date}")
            print(f"  Status: {meeting.status}")
            if meeting.summary:
                print(f"  Has minutes: Yes ({len(meeting.summary)} chars)")
            else:
                print(f"  Has minutes: No")

            # Show agenda items
            agenda_items = db.query(AgendaItem).filter(AgendaItem.meeting_id == meeting.id).all()
            print(f"  Agenda items: {len(agenda_items)}")

    except Exception as e:
        print(f"Error testing meeting scraper: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

async def test_specific_url():
    """Test scraping a specific URL"""
    print("\n" + "="*50)
    print("TESTING SPECIFIC URL SCRAPING")
    print("="*50)

    # You can modify this URL to test a specific meeting
    test_url = "https://tulsacouncil.org/meetings"  # Replace with actual meeting URL

    db = SessionLocal()
    try:
        scraper = MeetingScraper(db)
        meeting = await scraper.scrape_specific_meeting(test_url)

        if meeting:
            print(f"Successfully scraped: {meeting.title}")
        else:
            print("No meeting found at URL")

    except Exception as e:
        print(f"Error testing specific URL: {e}")
    finally:
        db.close()

def show_database_contents():
    """Show what's currently in the test database"""
    print("\n" + "="*50)
    print("DATABASE CONTENTS")
    print("="*50)

    db = SessionLocal()
    try:
        meetings = db.query(Meeting).all()

        if not meetings:
            print("No meetings in database")
            return

        for meeting in meetings:
            print(f"\nMeeting: {meeting.title}")
            print(f"  ID: {meeting.id}")
            print(f"  Date: {meeting.meeting_date}")
            print(f"  Location: {meeting.location}")
            print(f"  Type: {meeting.meeting_type}")
            print(f"  Status: {meeting.status}")
            print(f"  External ID: {meeting.external_id}")
            print(f"  Agenda URL: {meeting.agenda_url}")

            if meeting.summary:
                print(f"  Summary: {meeting.summary[:100]}...")

            # Show agenda items
            agenda_items = db.query(AgendaItem).filter(AgendaItem.meeting_id == meeting.id).all()
            if agenda_items:
                print(f"  Agenda Items ({len(agenda_items)}):")
                for item in agenda_items[:3]:  # Show first 3
                    print(f"    - {item.title}")
                if len(agenda_items) > 3:
                    print(f"    ... and {len(agenda_items) - 3} more")

    finally:
        db.close()

async def main():
    """Main test function"""
    print("CityCamp AI Scraper Test Suite")
    print("==============================")

    while True:
        print("\nChoose a test to run:")
        print("1. Test TGOV Scraper (direct)")
        print("2. Test Meeting Scraper (full workflow)")
        print("3. Test specific URL")
        print("4. Show database contents")
        print("5. Clear database")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            await test_tgov_scraper()
        elif choice == "2":
            await test_meeting_scraper()
        elif choice == "3":
            await test_specific_url()
        elif choice == "4":
            show_database_contents()
        elif choice == "5":
            # Clear database
            db = SessionLocal()
            try:
                db.query(AgendaItem).delete()
                db.query(Meeting).delete()
                db.commit()
                print("Database cleared!")
            finally:
                db.close()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
