from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class CampaignBase(BaseModel):
    title: str
    description: str
    short_description: Optional[str] = None
    category: str
    tags: List[str] = []
    goals: Optional[str] = None
    target_audience: Optional[str] = None
    target_signatures: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    contact_representatives: List[int] = []
    email_template: Optional[str] = None
    image_url: Optional[str] = None
    website_url: Optional[str] = None
    social_links: Dict[str, Any] = {}
    resources: List[str] = []
    is_public: bool = True
    allow_comments: bool = True
    allow_new_members: bool = True


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    goals: Optional[str] = None
    target_audience: Optional[str] = None
    status: Optional[str] = None
    target_signatures: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    contact_representatives: Optional[List[int]] = None
    email_template: Optional[str] = None
    image_url: Optional[str] = None
    website_url: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None
    resources: Optional[List[str]] = None
    is_public: Optional[bool] = None
    allow_comments: Optional[bool] = None
    allow_new_members: Optional[bool] = None
    featured: Optional[bool] = None


class CampaignResponse(CampaignBase):
    id: int
    creator_id: int
    status: str
    progress: int
    current_signatures: int
    views: int
    shares: int
    member_count: int
    featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # User's relationship to this campaign (if authenticated)
    is_member: Optional[bool] = None
    membership_role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignMembershipBase(BaseModel):
    campaign_id: int
    role: str = "member"
    receive_updates: bool = True
    receive_notifications: bool = True


class CampaignMembershipCreate(CampaignMembershipBase):
    pass


class CampaignMembershipUpdate(BaseModel):
    role: Optional[str] = None
    can_post_updates: Optional[bool] = None
    can_manage_members: Optional[bool] = None
    can_edit_campaign: Optional[bool] = None
    receive_updates: Optional[bool] = None
    receive_notifications: Optional[bool] = None


class CampaignMembershipResponse(CampaignMembershipBase):
    id: int
    user_id: int
    joined_at: datetime
    can_post_updates: bool
    can_manage_members: bool
    can_edit_campaign: bool
    last_active: Optional[datetime] = None
    contributions: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CampaignListResponse(BaseModel):
    campaigns: List[CampaignResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserCampaignSummary(BaseModel):
    """Summary of user's campaign subscriptions for dashboard"""

    total_subscribed: int
    active_campaigns: List[CampaignResponse]
    recent_updates: int
