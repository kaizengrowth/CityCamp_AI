#!/usr/bin/env python3
"""
Add sample meeting data to the main application database
This will populate the database with the same data from our test
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.config import settings
from app.models.meeting import Meeting, AgendaItem
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_meetings():
    """Create sample meetings in the main database"""

    # Use the same database as the main application
    DATABASE_URL = settings.database_url
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Clear existing sample data
        db.query(AgendaItem).filter(
            AgendaItem.meeting_id.in_(
                db.query(Meeting.id).filter(Meeting.source == "sample_data")
            )
        ).delete(synchronize_session=False)
        db.query(Meeting).filter(Meeting.source == "sample_data").delete()
        db.commit()

        # Create sample meetings
        meetings_data = [
            {
                "title": "Regular City Council Meeting",
                "meeting_date": datetime.now() - timedelta(days=7),
                "location": "One Technology Center, Tulsa, OK",
                "meeting_type": "regular_council",
                "status": "completed",
                "external_id": "sample-council-1",
                "source": "sample_data",
                "summary": """TULSA CITY COUNCIL MEETING MINUTES
January 15, 2025

CALL TO ORDER
The Regular Meeting of the Tulsa City Council was called to order at 5:00 PM by Council Chair.

ROLL CALL
Present: Councilors District 1-9
Absent: None

AGENDA ITEMS DISCUSSED:

1. BUDGET APPROPRIATIONS
   - Motion to approve $2.3M for street repairs
   - Passed 8-1

2. ZONING CHANGES
   - Rezoning request for 71st Street corridor
   - Public hearing held
   - Approved unanimously

3. PUBLIC SAFETY INITIATIVES
   - New police substations proposal
   - Community policing expansion
   - Approved with amendments

4. INFRASTRUCTURE PROJECTS
   - Bridge maintenance funding
   - Water system upgrades
   - Road resurfacing schedule

CITIZEN COMMENTS:
- 12 citizens spoke on various issues
- Main concerns: traffic, housing, parks

ADJOURNMENT: 7:45 PM

Meeting recorded and available online."""
            },
            {
                "title": "Public Works Committee Meeting",
                "meeting_date": datetime.now() - timedelta(days=3),
                "location": "City Hall Committee Room",
                "meeting_type": "public_works_committee",
                "status": "completed",
                "external_id": "sample-pw-1",
                "source": "sample_data",
                "summary": """PUBLIC WORKS COMMITTEE MINUTES
January 19, 2025

ATTENDEES:
Committee Chair, Committee Members, Public Works Director

AGENDA:

1. STREET MAINTENANCE REPORT
   - Winter road conditions update
   - Salt/sand usage statistics
   - Equipment status report

2. UPCOMING PROJECTS
   - Spring pothole repair schedule
   - Sidewalk improvement program
   - Traffic signal upgrades at 5 intersections

3. BUDGET REVIEW
   - Q1 spending analysis
   - Equipment replacement needs
   - Emergency repair fund status

4. CITIZEN REQUESTS
   - 23 new service requests reviewed
   - Priority ranking established
   - Response timeline set

ACTIONS TAKEN:
- Approved emergency road repair contract
- Authorized traffic study for Yale Avenue
- Scheduled public hearing for bike lane proposal

NEXT MEETING: February 2, 2025"""
            },
            {
                "title": "Urban & Economic Development Committee",
                "meeting_date": datetime.now() + timedelta(days=5),
                "location": "One Technology Center",
                "meeting_type": "urban_economic_committee",
                "status": "scheduled",
                "external_id": "sample-ued-1",
                "source": "sample_data"
            }
        ]

        created_meetings = []
        for meeting_data in meetings_data:
            meeting = Meeting(**meeting_data)
            db.add(meeting)
            db.flush()  # Get the ID
            created_meetings.append(meeting)

            # Add sample agenda items
            if meeting.meeting_type == "regular_council":
                agenda_items = [
                    {"title": "Budget Appropriations", "description": "Review and approve city budget items", "item_number": "1"},
                    {"title": "Zoning Changes", "description": "71st Street corridor rezoning proposal", "item_number": "2"},
                    {"title": "Public Safety", "description": "New police substation locations", "item_number": "3"},
                    {"title": "Citizen Comments", "description": "Public comment period", "item_number": "4"}
                ]
            elif meeting.meeting_type == "public_works_committee":
                agenda_items = [
                    {"title": "Street Maintenance", "description": "Winter road maintenance report", "item_number": "1"},
                    {"title": "Project Updates", "description": "Upcoming infrastructure projects", "item_number": "2"},
                    {"title": "Budget Review", "description": "Q1 budget analysis", "item_number": "3"}
                ]
            else:
                agenda_items = [
                    {"title": "Economic Development", "description": "New business incentives", "item_number": "1"},
                    {"title": "Urban Planning", "description": "Downtown revitalization", "item_number": "2"}
                ]

            for item_data in agenda_items:
                item_data["meeting_id"] = meeting.id
                agenda_item = AgendaItem(**item_data)
                db.add(agenda_item)

        db.commit()
        logger.info(f"✅ Successfully created {len(created_meetings)} sample meetings in main database")

        # Show what was created
        for meeting in created_meetings:
            logger.info(f"   📅 {meeting.title} ({meeting.meeting_date.strftime('%Y-%m-%d')})")

        return created_meetings

    except Exception as e:
        logger.error(f"❌ Error creating sample meetings: {e}")
        db.rollback()
        return []
    finally:
        db.close()

if __name__ == "__main__":
    print("🏛️  Adding sample meeting data to CityCamp AI database...")
    meetings = create_sample_meetings()

    if meetings:
        print(f"\n🎉 Success! Added {len(meetings)} meetings to the database.")
        print("You should now be able to see this data in the frontend!")
        print("\nTo test the API:")
        print("curl http://localhost:8000/api/v1/meetings/")
    else:
        print("\n❌ Failed to add sample data")
