from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


class TopicSubscriptionCreate(BaseModel):
    """Schema for creating a new topic subscription"""

    email: EmailStr
    phone_number: Optional[str] = None
    full_name: str
    zip_code: Optional[str] = None
    council_district: Optional[str] = None
    interested_topics: List[str] = []
    meeting_types: List[str] = []
    sms_notifications: bool = True
    email_notifications: bool = True
    advance_notice_hours: int = 24
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str = "America/Chicago"
    digest_mode: bool = False

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v and not v.startswith("+"):
            # Simple validation - in production, use a proper phone number library
            digits_only = "".join(filter(str.isdigit, v))
            if len(digits_only) < 10:
                raise ValueError("Phone number must be at least 10 digits")
        return v

    @field_validator("advance_notice_hours")
    @classmethod
    def validate_advance_notice(cls, v):
        if v < 1 or v > 168:  # 1 hour to 1 week
            raise ValueError("Advance notice must be between 1 and 168 hours")
        return v


class TopicSubscriptionResponse(BaseModel):
    """Schema for topic subscription responses"""

    id: int
    email: str
    phone_number: Optional[str]
    full_name: str
    zip_code: Optional[str]
    council_district: Optional[str]
    interested_topics: List[str]
    meeting_types: List[str]
    sms_notifications: bool
    email_notifications: bool
    is_active: bool
    confirmed: bool
    advance_notice_hours: int
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    timezone: str
    digest_mode: bool
    total_notifications_sent: int
    created_at: datetime
    updated_at: Optional[datetime]
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TopicSubscriptionUpdate(BaseModel):
    """Schema for updating topic subscription preferences"""

    interested_topics: Optional[List[str]] = None
    meeting_types: Optional[List[str]] = None
    sms_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    is_active: Optional[bool] = None
    advance_notice_hours: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    digest_mode: Optional[bool] = None

    @field_validator("advance_notice_hours")
    @classmethod
    def validate_advance_notice(cls, v):
        if v is not None and (v < 1 or v > 168):
            raise ValueError("Advance notice must be between 1 and 168 hours")
        return v


class MeetingTopicResponse(BaseModel):
    """Schema for meeting topic responses"""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    keywords: List[str]
    category: Optional[str]
    icon: Optional[str]
    color: Optional[str]
    is_active: bool
    subscriber_count: int
    # Removed created_at and updated_at to avoid datetime serialization issues
    # Frontend doesn't need these fields for topic display

    class Config:
        from_attributes = True


class MeetingTopicCreate(BaseModel):
    """Schema for creating meeting topics (admin only)"""

    name: str
    display_name: str
    description: Optional[str] = None
    keywords: List[str] = []
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class SubscriptionConfirmRequest(BaseModel):
    """Schema for confirming email/phone subscriptions"""

    email: EmailStr
    verification_token: str


class NotificationPreview(BaseModel):
    """Schema for previewing notifications that would be sent"""

    meeting_title: str
    meeting_date: datetime
    topics_matched: List[str]
    meeting_type: str
    location: str
    advance_notice_hours: int


class SubscriptionStatsResponse(BaseModel):
    """Schema for subscription statistics"""

    total_subscriptions: int
    active_subscriptions: int
    confirmed_subscriptions: int
    sms_subscribers: int
    email_subscribers: int
    top_topics: List[dict]  # [{topic: str, count: int}]
    recent_signups: int  # Last 30 days
