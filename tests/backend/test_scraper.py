#!/usr/bin/env python3
"""
Test script for the CityCamp AI scraper
"""

import pytest
from app.models.meeting import Meeting, AgendaItem

def test_meeting_model(db_session):
    """Test the Meeting model creation and basic operations"""
    # Create a test meeting
    meeting = Meeting(
        title="Test City Council Meeting",
        meeting_type="city_council",
        meeting_date="2025-01-15 14:00:00",
        location="City Hall",
        source="test_scraper",
        external_id="test-2025-01-15"
    )

    db_session.add(meeting)
    db_session.commit()
    db_session.refresh(meeting)

    # Verify the meeting was created
    assert meeting.id is not None
    assert meeting.title == "Test City Council Meeting"
    assert meeting.meeting_type == "city_council"
    assert meeting.status == "scheduled"

def test_agenda_item_model(db_session):
    """Test the AgendaItem model creation"""
    # Create a test meeting first
    meeting = Meeting(
        title="Test Meeting",
        meeting_type="city_council",
        meeting_date="2025-01-15 14:00:00",
        source="test_scraper"
    )
    db_session.add(meeting)
    db_session.commit()

    # Create an agenda item
    agenda_item = AgendaItem(
        meeting_id=meeting.id,
        item_number="1.A",
        title="Test Ordinance",
        description="A test ordinance for testing purposes",
        item_type="ordinance"
    )

    db_session.add(agenda_item)
    db_session.commit()
    db_session.refresh(agenda_item)

    # Verify the agenda item was created
    assert agenda_item.id is not None
    assert agenda_item.meeting_id == meeting.id
    assert agenda_item.title == "Test Ordinance"

def test_meeting_relationships(db_session):
    """Test meeting and agenda item relationships"""
    # Create a meeting with agenda items
    meeting = Meeting(
        title="Test Meeting with Items",
        meeting_type="city_council",
        meeting_date="2025-01-15 14:00:00",
        source="test_scraper"
    )
    db_session.add(meeting)
    db_session.commit()

    # Create agenda items
    item1 = AgendaItem(
        meeting_id=meeting.id,
        item_number="1.A",
        title="First Item",
        item_type="ordinance"
    )
    item2 = AgendaItem(
        meeting_id=meeting.id,
        item_number="1.B",
        title="Second Item",
        item_type="resolution"
    )

    db_session.add_all([item1, item2])
    db_session.commit()

    # Test relationship
    assert len(meeting.agenda_items) == 2
    assert meeting.agenda_items[0].title == "First Item"
    assert meeting.agenda_items[1].title == "Second Item"
