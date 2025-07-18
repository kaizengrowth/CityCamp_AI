import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
from sqlalchemy.orm import Session
from app.models.meeting import Meeting, AgendaItem
from app.models.user import User
from app.models.notification import Notification

logger = logging.getLogger(__name__)

class TGOVScraper:
    """
    TGOV Scraper for Tulsa City Council meetings
    Adapted from your existing tgov_scraper_api scripts
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://tulsacouncil.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CityCamp AI Bot 1.0'
        })
    
    async def scrape_upcoming_meetings(self, days_ahead: int = 30) -> List[Meeting]:
        """
        Scrape upcoming meetings from Tulsa City Council website
        Based on your existing scripts
        """
        try:
            meetings = []
            
            # Get the meetings page
            meetings_url = f"{self.base_url}/meetings"
            response = self.session.get(meetings_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse meeting information
            # This would be adapted from your specific scraping logic
            meeting_elements = soup.find_all('div', class_='meeting-item')  # Adjust selector
            
            for element in meeting_elements:
                meeting_data = await self._parse_meeting_element(element)
                if meeting_data:
                    meeting = await self._create_or_update_meeting(meeting_data)
                    meetings.append(meeting)
            
            return meetings
            
        except Exception as e:
            logger.error(f"Error scraping meetings: {str(e)}")
            return []
    
    async def _parse_meeting_element(self, element) -> Optional[Dict]:
        """Parse individual meeting element from HTML"""
        try:
            # Extract meeting details - adapt this to match actual HTML structure
            title_elem = element.find('h3') or element.find('h2')
            title = title_elem.text.strip() if title_elem else "City Council Meeting"
            
            date_elem = element.find('time') or element.find('span', class_='date')
            date_str = date_elem.get('datetime') or date_elem.text.strip() if date_elem else None
            
            if not date_str:
                return None
            
            # Parse date - adapt format as needed
            try:
                meeting_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                # Try alternative date formats
                meeting_date = self._parse_flexible_date(date_str)
                if not meeting_date:
                    return None
            
            # Extract other details
            location_elem = element.find('span', class_='location')
            location = location_elem.text.strip() if location_elem else "City Hall"
            
            agenda_link = element.find('a', href=re.compile(r'agenda|pdf'))
            agenda_url = agenda_link.get('href') if agenda_link else None
            if agenda_url and not agenda_url.startswith('http'):
                agenda_url = f"{self.base_url}{agenda_url}"
            
            # Extract meeting type
            meeting_type = "city_council"
            if "planning" in title.lower():
                meeting_type = "planning_commission"
            elif "committee" in title.lower():
                meeting_type = "committee"
            
            return {
                'title': title,
                'meeting_date': meeting_date,
                'location': location,
                'agenda_url': agenda_url,
                'meeting_type': meeting_type,
                'external_id': f"tulsa-{meeting_date.strftime('%Y-%m-%d')}-{meeting_type}"
            }
            
        except Exception as e:
            logger.error(f"Error parsing meeting element: {str(e)}")
            return None
    
    def _parse_flexible_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple possible formats"""
        formats = [
            "%B %d, %Y at %I:%M %p",
            "%B %d, %Y %I:%M %p",
            "%m/%d/%Y %I:%M %p",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    async def _create_or_update_meeting(self, meeting_data: Dict) -> Meeting:
        """Create or update meeting in database"""
        existing_meeting = self.db.query(Meeting).filter(
            Meeting.external_id == meeting_data['external_id']
        ).first()
        
        if existing_meeting:
            # Update existing meeting
            existing_meeting.title = meeting_data['title']
            existing_meeting.meeting_date = meeting_data['meeting_date']
            existing_meeting.location = meeting_data['location']
            existing_meeting.agenda_url = meeting_data['agenda_url']
            existing_meeting.meeting_type = meeting_data['meeting_type']
            meeting = existing_meeting
        else:
            # Create new meeting
            meeting = Meeting(
                external_id=meeting_data['external_id'],
                title=meeting_data['title'],
                meeting_date=meeting_data['meeting_date'],
                location=meeting_data['location'],
                agenda_url=meeting_data['agenda_url'],
                meeting_type=meeting_data['meeting_type'],
                source="tgov_scraper",
                status="scheduled"
            )
            self.db.add(meeting)
        
        self.db.commit()
        self.db.refresh(meeting)
        return meeting
    
    async def scrape_meeting_minutes(self, meeting: Meeting) -> Optional[str]:
        """
        Scrape meeting minutes/transcript
        Based on your existing minutes scraping logic
        """
        try:
            if not meeting.agenda_url:
                return None
            
            # Get the meeting page
            response = self.session.get(meeting.agenda_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for minutes link
            minutes_link = soup.find('a', href=re.compile(r'minutes|transcript'))
            if not minutes_link:
                return None
            
            minutes_url = minutes_link.get('href')
            if not minutes_url.startswith('http'):
                minutes_url = f"{self.base_url}{minutes_url}"
            
            # Download minutes
            minutes_response = self.session.get(minutes_url)
            minutes_response.raise_for_status()
            
            # Extract text content
            if minutes_url.endswith('.pdf'):
                # Handle PDF extraction - you might need pdfplumber or similar
                return "PDF minutes available at: " + minutes_url
            else:
                # Handle HTML minutes
                minutes_soup = BeautifulSoup(minutes_response.content, 'html.parser')
                
                # Remove navigation and other non-content elements
                for element in minutes_soup(['nav', 'header', 'footer', 'aside']):
                    element.decompose()
                
                # Extract main content
                content_div = minutes_soup.find('div', class_='content') or minutes_soup.find('main')
                if content_div:
                    return content_div.get_text(strip=True)
                else:
                    return minutes_soup.get_text(strip=True)
            
        except Exception as e:
            logger.error(f"Error scraping minutes for meeting {meeting.id}: {str(e)}")
            return None
    
    async def scrape_agenda_items(self, meeting: Meeting) -> List[AgendaItem]:
        """
        Scrape agenda items for a meeting
        Based on your existing agenda parsing logic
        """
        try:
            if not meeting.agenda_url:
                return []
            
            response = self.session.get(meeting.agenda_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            agenda_items = []
            
            # Look for agenda items - adapt selectors based on actual HTML structure
            item_elements = soup.find_all(['li', 'div'], class_=re.compile(r'agenda|item'))
            
            for i, element in enumerate(item_elements):
                item_data = self._parse_agenda_item(element, i + 1)
                if item_data:
                    agenda_item = AgendaItem(
                        meeting_id=meeting.id,
                        item_number=item_data['item_number'],
                        title=item_data['title'],
                        description=item_data.get('description'),
                        item_type=item_data.get('item_type', 'general')
                    )
                    self.db.add(agenda_item)
                    agenda_items.append(agenda_item)
            
            self.db.commit()
            return agenda_items
            
        except Exception as e:
            logger.error(f"Error scraping agenda items for meeting {meeting.id}: {str(e)}")
            return []
    
    def _parse_agenda_item(self, element, item_number: int) -> Optional[Dict]:
        """Parse individual agenda item"""
        try:
            title_elem = element.find(['h3', 'h4', 'strong']) or element
            title = title_elem.get_text(strip=True)
            
            if not title or len(title) < 10:  # Skip very short items
                return None
            
            # Extract item number if present
            number_match = re.match(r'^(\d+\.?\w*\.?)\s*', title)
            if number_match:
                item_num = number_match.group(1)
                title = title[len(item_num):].strip()
            else:
                item_num = str(item_number)
            
            # Extract description
            description = None
            desc_elem = element.find('p') or element.find('div', class_='description')
            if desc_elem:
                description = desc_elem.get_text(strip=True)
            
            return {
                'item_number': item_num,
                'title': title,
                'description': description
            }
            
        except Exception as e:
            logger.error(f"Error parsing agenda item: {str(e)}")
            return None 