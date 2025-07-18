import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.meeting import Meeting, AgendaItem
from app.core.database import get_db

logger = logging.getLogger(__name__)

class TGOVIntegrationService:
    """Service to integrate with Code for Tulsa's TGOV scraper data"""
    
    def __init__(self, db: Session):
        self.db = db
        # These would be the actual endpoints from the tgov-scraper project
        self.tgov_api_base = "https://api.tgov-scraper.codefortulsa.org"  # Hypothetical API
        self.granicus_base = "https://archive-stream.granicus.com"
        
    async def fetch_meetings_from_tgov(self) -> List[Dict]:
        """Fetch meeting data from TGOV scraper registry"""
        try:
            # This would connect to the actual tgov-scraper data
            # For now, we'll simulate the data structure they would provide
            
            # In reality, you'd either:
            # 1. Connect to their database/API if they expose one
            # 2. Run their scraper workflows and read the registry
            # 3. Fork their project and add an API layer
            
            mock_tgov_data = [
                {
                    "meeting_id": "tulsa-council-2024-01-15",
                    "title": "City Council Regular Meeting",
                    "date": "2024-01-15T19:00:00Z",
                    "video_url": "https://archive-stream.granicus.com/OnDemand/_definst_/mp4:archive/tulsa-ok/tulsa-ok_843d30f2.mp4/playlist.m3u8",
                    "transcription_url": "https://data.tgov-scraper.org/transcriptions/2024-01-15.txt",
                    "subtitled_video_url": "https://data.tgov-scraper.org/videos/2024-01-15-subtitled.html",
                    "translated_transcriptions": {
                        "es": "https://data.tgov-scraper.org/transcriptions/2024-01-15-es.txt",
                        "mya": "https://data.tgov-scraper.org/transcriptions/2024-01-15-mya.txt"
                    },
                    "agenda_items": [
                        {
                            "item_number": "1.A",
                            "title": "Budget Amendment for Infrastructure",
                            "description": "Proposed budget amendment for street repairs",
                            "keywords": ["budget", "infrastructure", "streets"]
                        },
                        {
                            "item_number": "2.B", 
                            "title": "Zoning Variance Request",
                            "description": "Commercial zoning variance for downtown development",
                            "keywords": ["zoning", "development", "downtown"]
                        }
                    ]
                }
            ]
            
            return mock_tgov_data
            
        except Exception as e:
            logger.error(f"Error fetching TGOV data: {str(e)}")
            return []
    
    async def sync_meeting_with_tgov_data(self, tgov_meeting: Dict) -> Meeting:
        """Create or update a meeting with TGOV scraper data"""
        
        # Check if meeting already exists
        existing_meeting = self.db.query(Meeting).filter(
            Meeting.external_id == tgov_meeting["meeting_id"]
        ).first()
        
        # Parse the meeting date
        meeting_date = datetime.fromisoformat(
            tgov_meeting["date"].replace('Z', '+00:00')
        )
        
        if existing_meeting:
            # Update existing meeting with TGOV data
            existing_meeting.title = tgov_meeting["title"]
            existing_meeting.meeting_date = meeting_date
            existing_meeting.meeting_url = tgov_meeting.get("video_url")
            existing_meeting.source = "tgov_scraper"
            
            # Add TGOV-specific data
            if tgov_meeting.get("transcription_url"):
                # You could store transcription content or URL
                existing_meeting.summary = f"Transcription available: {tgov_meeting['transcription_url']}"
            
            meeting = existing_meeting
        else:
            # Create new meeting
            meeting = Meeting(
                external_id=tgov_meeting["meeting_id"],
                title=tgov_meeting["title"],
                meeting_type="city_council",
                meeting_date=meeting_date,
                meeting_url=tgov_meeting.get("video_url"),
                source="tgov_scraper",
                summary=f"Transcription available: {tgov_meeting.get('transcription_url', 'N/A')}"
            )
            self.db.add(meeting)
        
        # Sync agenda items
        if tgov_meeting.get("agenda_items"):
            await self.sync_agenda_items(meeting, tgov_meeting["agenda_items"])
        
        self.db.commit()
        self.db.refresh(meeting)
        return meeting
    
    async def sync_agenda_items(self, meeting: Meeting, agenda_items: List[Dict]):
        """Sync agenda items for a meeting"""
        for item_data in agenda_items:
            existing_item = self.db.query(AgendaItem).filter(
                AgendaItem.meeting_id == meeting.id,
                AgendaItem.item_number == item_data["item_number"]
            ).first()
            
            if existing_item:
                # Update existing item
                existing_item.title = item_data["title"]
                existing_item.description = item_data.get("description")
                existing_item.keywords = item_data.get("keywords", [])
            else:
                # Create new agenda item
                agenda_item = AgendaItem(
                    meeting_id=meeting.id,
                    item_number=item_data["item_number"],
                    title=item_data["title"],
                    description=item_data.get("description"),
                    keywords=item_data.get("keywords", [])
                )
                self.db.add(agenda_item)
    
    async def download_transcription(self, transcription_url: str) -> Optional[str]:
        """Download and return transcription content"""
        try:
            response = requests.get(transcription_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error downloading transcription: {str(e)}")
            return None
    
    async def get_meeting_transcription(self, meeting_id: str) -> Optional[str]:
        """Get transcription for a specific meeting"""
        # This would look up the transcription URL from the TGOV registry
        # and download the content
        meeting = self.db.query(Meeting).filter(
            Meeting.external_id == meeting_id
        ).first()
        
        if meeting and meeting.summary and "Transcription available:" in meeting.summary:
            transcription_url = meeting.summary.split("Transcription available: ")[1]
            return await self.download_transcription(transcription_url)
        
        return None 