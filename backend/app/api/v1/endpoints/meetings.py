from datetime import datetime, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.models.meeting import Meeting
from app.models.user import User
from app.services.auth import get_current_user
from app.services.meeting_service import MeetingService
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()


# Pydantic schemas
class MeetingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    meeting_type: str
    meeting_date: datetime
    location: Optional[str]
    meeting_url: Optional[str]
    agenda_url: Optional[str]
    status: str
    topics: List[str]
    summary: Optional[str]  # Meeting minutes/summary
    source: Optional[str]  # Source of the meeting data

    class Config:
        from_attributes = True


class AgendaItemResponse(BaseModel):
    id: int
    item_number: Optional[str]
    title: str
    description: Optional[str]
    item_type: Optional[str]
    category: Optional[str]
    keywords: List[str]
    summary: Optional[str]  # Agenda item summary

    class Config:
        from_attributes = True


class MeetingWithAgenda(MeetingResponse):
    agenda_items: List[AgendaItemResponse]


@router.get("/all", response_model=List[MeetingResponse])
async def get_all_meetings(
    db: Session = Depends(get_db),
    limit: int = Query(100, le=500, description="Maximum number of meetings to return"),
    offset: int = Query(0, ge=0, description="Number of meetings to skip"),
):
    """Get all meetings without date filtering"""
    meeting_service = MeetingService(db)
    meetings = (
        db.query(Meeting)
        .order_by(Meeting.meeting_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return meetings


@router.get("/public", response_model=List[MeetingResponse])
async def get_meetings_public(
    db: Session = Depends(get_db),
    limit: int = Query(10, le=50, description="Maximum number of meetings to return"),
):
    """Get meetings - public endpoint (no auth required)"""
    meeting_service = MeetingService(db)
    meetings = await meeting_service.get_meetings_by_date_range(
        datetime.now() - timedelta(days=90), datetime.now() + timedelta(days=90)
    )
    return meetings[:limit]


@router.get("/", response_model=List[MeetingResponse])
async def get_meetings(
    db: Session = Depends(get_db),
    meeting_type: Optional[str] = Query(None, description="Filter by meeting type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, le=100, description="Maximum number of meetings to return"),
):
    """Get meetings with optional filters"""
    meeting_service = MeetingService(db)

    if start_date and end_date:
        meetings = await meeting_service.get_meetings_by_date_range(
            start_date, end_date
        )
    elif meeting_type:
        meetings = await meeting_service.get_meetings_by_type(meeting_type)
    else:
        # Default to upcoming meetings
        meetings = await meeting_service.get_meetings_by_date_range(
            datetime.now(), datetime.now() + timedelta(days=30)
        )

    return meetings[:limit]


@router.get("/upcoming", response_model=List[MeetingResponse])
async def get_upcoming_meetings(
    db: Session = Depends(get_db),
    days_ahead: int = Query(30, le=90, description="Number of days ahead to fetch"),
):
    """Get upcoming meetings"""
    meeting_service = MeetingService(db)
    meetings = await meeting_service.get_meetings_by_date_range(
        datetime.now(), datetime.now() + timedelta(days=days_ahead)
    )
    return meetings


@router.get("/my-interests", response_model=List[MeetingResponse])
async def get_meetings_for_user_interests(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get meetings relevant to user's interests"""
    meeting_service = MeetingService(db)
    meetings = await meeting_service.get_user_relevant_meetings(current_user.interests)
    return meetings


@router.get("/{meeting_id}", response_model=MeetingWithAgenda)
async def get_meeting_detail(meeting_id: int, db: Session = Depends(get_db)):
    """Get detailed meeting information including agenda items"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting


@router.get("/search", response_model=List[MeetingResponse])
async def search_meetings(
    q: str = Query(..., description="Search query"), db: Session = Depends(get_db)
):
    """Search meetings by topic or keyword"""
    meeting_service = MeetingService(db)
    meetings = await meeting_service.search_meetings_by_topic(q)
    return meetings


@router.post("/sync")
async def sync_meetings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Sync meetings from external API (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    meeting_service = MeetingService(db)
    meetings = await meeting_service.fetch_upcoming_meetings()

    return {"message": f"Synced {len(meetings)} meetings", "meetings": meetings}


@router.get("/types", response_model=List[str])
async def get_meeting_types(db: Session = Depends(get_db)):
    """Get available meeting types"""
    types = db.query(Meeting.meeting_type).distinct().all()
    return [t[0] for t in types]


@router.get("/categories", response_model=List[str])
async def get_meeting_categories(db: Session = Depends(get_db)):
    """Get available meeting categories/topics"""
    # Get all unique topics from meetings
    meetings = db.query(Meeting).all()
    topics = set()
    for meeting in meetings:
        if meeting.topics:
            topics.update(meeting.topics)

    return sorted(list(topics))
