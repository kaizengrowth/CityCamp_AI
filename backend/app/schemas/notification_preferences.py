from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NotificationPreferencesBase(BaseModel):
    """Base notification preferences schema"""

    # Contact information
    email: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: str

    # Location information
    zip_code: Optional[str] = None
    council_district: Optional[str] = None

    # Notification channels
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = False

    # Content preferences
    interested_topics: List[str] = Field(default_factory=list)
    meeting_types: List[str] = Field(default_factory=list)

    # Timing preferences
    advance_notice_hours: int = 24
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str = "America/Chicago"

    # Frequency preferences
    digest_mode: bool = False
    max_notifications_per_day: int = 5


class NotificationPreferencesCreate(NotificationPreferencesBase):
    """Schema for creating notification preferences"""

    pass


class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating notification preferences"""

    # Contact information
    phone_number: Optional[str] = None
    full_name: Optional[str] = None

    # Location information
    zip_code: Optional[str] = None
    council_district: Optional[str] = None

    # Notification channels
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None

    # Content preferences
    interested_topics: Optional[List[str]] = None
    meeting_types: Optional[List[str]] = None

    # Timing preferences
    advance_notice_hours: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

    # Frequency preferences
    digest_mode: Optional[bool] = None
    max_notifications_per_day: Optional[int] = None


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Schema for notification preferences responses"""

    id: int
    user_id: Optional[int] = None

    # Status and verification
    is_active: bool
    email_verified: bool
    phone_verified: bool

    # Tracking
    source: str
    last_notified: Optional[datetime] = None
    total_notifications_sent: int

    # Metadata
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferencesList(BaseModel):
    """Schema for notification preferences list response"""

    preferences: List[NotificationPreferencesResponse]
    total: int
    skip: int
    limit: int
