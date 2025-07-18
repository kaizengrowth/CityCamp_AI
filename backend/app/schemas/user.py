from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    phone_number: Optional[str] = None
    interests: List[str] = []
    zip_code: Optional[str] = None
    council_district: Optional[str] = None


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    interests: Optional[List[str]] = None
    zip_code: Optional[str] = None
    council_district: Optional[str] = None
    sms_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_admin: bool
    sms_notifications: bool
    email_notifications: bool
    push_notifications: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None


class UserInterestCreate(BaseModel):
    category: str
    keywords: List[str] = []
    priority: int = 1
    
    @validator('priority')
    def validate_priority(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Priority must be between 1 and 5')
        return v


class UserInterestResponse(BaseModel):
    id: int
    user_id: int
    category: str
    keywords: List[str]
    priority: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInterestUpdate(BaseModel):
    keywords: Optional[List[str]] = None
    priority: Optional[int] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Priority must be between 1 and 5')
        return v 