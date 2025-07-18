from datetime import datetime, timedelta
from typing import List, Optional
import requests
import logging
from sqlalchemy.orm import Session
from app.models.meeting import Meeting, AgendaItem, MeetingCategory
from app.core.database import get_db

logger = logging.getLogger(__name__)

class MeetingService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://api.tulsacouncil.org"  # Update with actual API endpoint
        
    async def fetch_upcoming_meetings(self, days_ahead: int = 30) -> List[Meeting]:
        """Fetch upcoming meetings from Tulsa City Council API"""
        try:
            # This would integrate with actual Tulsa City Council API
            # For now, we'll create a mock implementation
            end_date = datetime.now() + timedelta(days=days_ahead)
            
            # Mock data - replace with actual API call
            mock_meetings = [
                {
                    "id": "council-2024-01-15",
                    "title": "Tulsa City Council Regular Meeting",
                    "description": "Regular monthly city council meeting",
                    "meeting_type": "city_council",
                    "meeting_date": "2024-01-15T19:00:00",
                    "location": "City Hall Council Chambers",
                    "agenda_url": "https://www.cityoftulsa.org/agenda-2024-01-15.pdf",
                    "topics": ["budget", "zoning", "infrastructure"]
                },
                {
                    "id": "planning-2024-01-18",
                    "title": "Planning Commission Meeting",
                    "description": "Monthly planning commission meeting",
                    "meeting_type": "committee",
                    "meeting_date": "2024-01-18T17:30:00",
                    "location": "City Hall Conference Room A",
                    "agenda_url": "https://www.cityoftulsa.org/planning-agenda-2024-01-18.pdf",
                    "topics": ["development", "zoning", "permits"]
                }
            ]
            
            meetings = []
            for meeting_data in mock_meetings:
                meeting = await self.create_or_update_meeting(meeting_data)
                meetings.append(meeting)
                
            return meetings
            
        except Exception as e:
            logger.error(f"Error fetching meetings: {str(e)}")
            return []
    
    async def create_or_update_meeting(self, meeting_data: dict) -> Meeting:
        """Create or update a meeting in the database"""
        existing_meeting = self.db.query(Meeting).filter(
            Meeting.external_id == meeting_data["id"]
        ).first()
        
        if existing_meeting:
            # Update existing meeting
            for key, value in meeting_data.items():
                if key == "meeting_date":
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                setattr(existing_meeting, key, value)
            meeting = existing_meeting
        else:
            # Create new meeting
            meeting_data["meeting_date"] = datetime.fromisoformat(
                meeting_data["meeting_date"].replace('Z', '+00:00')
            )
            meeting = Meeting(
                external_id=meeting_data["id"],
                title=meeting_data["title"],
                description=meeting_data.get("description"),
                meeting_type=meeting_data["meeting_type"],
                meeting_date=meeting_data["meeting_date"],
                location=meeting_data.get("location"),
                agenda_url=meeting_data.get("agenda_url"),
                topics=meeting_data.get("topics", []),
                source="tulsa_city_council_api"
            )
            self.db.add(meeting)
        
        self.db.commit()
        self.db.refresh(meeting)
        return meeting
    
    async def get_meetings_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Meeting]:
        """Get meetings within a date range"""
        return self.db.query(Meeting).filter(
            Meeting.meeting_date >= start_date,
            Meeting.meeting_date <= end_date
        ).all()
    
    async def get_meetings_by_type(self, meeting_type: str) -> List[Meeting]:
        """Get meetings by type"""
        return self.db.query(Meeting).filter(
            Meeting.meeting_type == meeting_type
        ).all()
    
    async def search_meetings_by_topic(self, topic: str) -> List[Meeting]:
        """Search meetings by topic/keyword"""
        return self.db.query(Meeting).filter(
            Meeting.topics.contains([topic])
        ).all()
    
    async def get_user_relevant_meetings(self, user_interests: List[str]) -> List[Meeting]:
        """Get meetings relevant to user's interests"""
        upcoming_meetings = await self.get_meetings_by_date_range(
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )
        
        relevant_meetings = []
        for meeting in upcoming_meetings:
            if any(interest in meeting.topics for interest in user_interests):
                relevant_meetings.append(meeting)
        
        return relevant_meetings 