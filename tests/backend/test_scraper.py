#!/usr/bin/env python3
"""
Local test script for the CityCamp AI scraper
Run this to test scraper functionality without the full API
"""

import pytest
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

@pytest.fixture(scope="function")
def db_session():
    """Create a database session for testing"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    yield session

    # Cleanup
    session.query(AgendaItem).delete()
    session.query(Meeting).delete()
    session.commit()
    session.close()

@pytest.mark.asyncio
async def test_tgov_scraper(db_session):
    """Test the TGOV scraper directly"""
    scraper = TGOVScraper(db_session)

    # Test upcoming meetings scrape
    meetings = await scraper.scrape_upcoming_meetings(days_ahead=30)
    assert isinstance(meetings, list)

    # If meetings are found, test agenda items
    if meetings:
        meeting = meetings[0]
        agenda_items = await scraper.scrape_agenda_items(meeting)
        assert isinstance(agenda_items, list)

@pytest.mark.asyncio
async def test_meeting_scraper(db_session):
    """Test the full meeting scraper workflow"""
    scraper = MeetingScraper(db_session)

    # Run full scrape cycle
    stats = await scraper.run_full_scrape(days_ahead=30)

    # Verify stats structure
    expected_keys = [
        "meetings_found", "meetings_updated", "agenda_items_created",
        "minutes_scraped", "notifications_sent"
    ]
    for key in expected_keys:
        assert key in stats
        assert isinstance(stats[key], int)

@pytest.mark.asyncio
async def test_specific_url(db_session):
    """Test scraping a specific URL"""
    scraper = MeetingScraper(db_session)

    # Test with a dummy URL (this will likely return None, which is expected)
    test_url = "https://example.com/test-meeting"
    meeting = await scraper.scrape_specific_meeting(test_url)

    # The result should be None for a dummy URL, which is acceptable
    assert meeting is None or isinstance(meeting, Meeting)
