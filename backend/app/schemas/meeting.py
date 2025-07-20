from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class MeetingResponse(BaseModel):
    """Base response model for meeting data"""

    id: int
    title: str
    description: Optional[str]
    meeting_type: str
    meeting_date: datetime
    location: Optional[str]
    meeting_url: Optional[str]
    agenda_url: Optional[str]
    minutes_url: Optional[str]
    status: str
    external_id: Optional[str]
    source: str
    topics: List[str] = []
    keywords: List[str] = []
    summary: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class AgendaItemResponse(BaseModel):
    """Response model for agenda items"""

    id: int
    meeting_id: int
    item_number: Optional[str]
    title: str
    description: Optional[str]
    item_type: Optional[str]
    category: Optional[str]
    keywords: List[str] = []
    summary: Optional[str]
    impact_assessment: Optional[str]
    vote_required: bool = False
    vote_result: Optional[str]
    vote_details: Optional[Dict[str, Any]]
    attachments: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    """Response model for meeting categories"""

    id: int
    name: str
    description: Optional[str]
    keywords: List[str] = []
    color: Optional[str]
    icon: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class MeetingDetailResponse(BaseModel):
    """Detailed response model for individual meeting with agenda items"""

    meeting: MeetingResponse
    agenda_items: List[AgendaItemResponse] = []
    categories: List[CategoryResponse] = []
    pdf_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MeetingListResponse(BaseModel):
    """Response model for paginated meeting lists"""

    meetings: List[MeetingResponse]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(from_attributes=True)


class MeetingFilterParams(BaseModel):
    """Filter parameters for meeting queries"""

    meeting_type: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    search: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MeetingCreate(BaseModel):
    """Schema for creating new meetings"""

    title: str
    description: Optional[str] = None
    meeting_type: str
    meeting_date: datetime
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    agenda_url: Optional[str] = None
    minutes_url: Optional[str] = None
    external_id: Optional[str] = None
    source: str
    topics: List[str] = []
    keywords: List[str] = []
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MeetingUpdate(BaseModel):
    """Schema for updating meetings"""

    title: Optional[str] = None
    description: Optional[str] = None
    meeting_type: Optional[str] = None
    meeting_date: Optional[datetime] = None
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    agenda_url: Optional[str] = None
    minutes_url: Optional[str] = None
    status: Optional[str] = None
    topics: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
