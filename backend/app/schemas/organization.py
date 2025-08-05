from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[HttpUrl] = None
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    
    organization_type: str = Field(..., max_length=100)
    focus_areas: List[str] = Field(default_factory=list)
    service_areas: List[str] = Field(default_factory=list)
    
    facebook_url: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = Field(None, max_length=100)
    instagram_handle: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[HttpUrl] = None
    
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    member_count: Optional[int] = Field(None, ge=0)
    
    @field_validator('twitter_handle', 'instagram_handle')
    @classmethod
    def validate_social_handles(cls, v):
        if v and v.startswith('@'):
            return v[1:]  # Remove @ symbol if present
        return v


class OrganizationCreate(OrganizationBase):
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must only contain letters, numbers, and hyphens')
        return v.lower()


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[HttpUrl] = None
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    
    organization_type: Optional[str] = Field(None, max_length=100)
    focus_areas: Optional[List[str]] = None
    service_areas: Optional[List[str]] = None
    
    facebook_url: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = Field(None, max_length=100)
    instagram_handle: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[HttpUrl] = None
    
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    member_count: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class OrganizationInDB(OrganizationBase):
    id: int
    slug: str
    is_active: bool
    is_verified: bool
    has_account: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class Organization(OrganizationInDB):
    """Public organization response model"""
    pass


class OrganizationSummary(BaseModel):
    """Lightweight organization model for lists"""
    id: int
    name: str
    slug: str
    short_description: Optional[str]
    organization_type: Optional[str]
    focus_areas: Optional[List[str]]
    website_url: Optional[HttpUrl]
    is_verified: bool
    member_count: Optional[int]
    
    class Config:
        from_attributes = True


class OrganizationList(BaseModel):
    """Response model for organization list endpoint"""
    organizations: List[OrganizationSummary]
    total: int
    skip: int
    limit: int 