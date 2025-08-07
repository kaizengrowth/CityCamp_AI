from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard pagination parameters"""

    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")


class StandardListResponse(BaseModel, Generic[T]):
    """Standardized list response format"""

    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, items: List[T], total: int, skip: int, limit: int):
        """Create a standardized list response"""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total,
            has_prev=skip > 0,
        )


class StandardResponse(BaseModel, Generic[T]):
    """Standardized single item response format"""

    data: T
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standardized error response format"""

    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Standard health check response"""

    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    features: Dict[str, bool] = Field(default_factory=dict)
