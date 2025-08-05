from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    title: str
    document_type: str
    category: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None
    document_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    tags: List[str] = []
    keywords: List[str] = []
    is_public: bool = True


class DocumentCreate(DocumentBase):
    content: str
    file_name: str
    file_size: int
    mime_type: str
    uploaded_by: int


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    source_url: Optional[str] = None
    document_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    is_public: Optional[bool] = None


class DocumentResponse(DocumentBase):
    id: int
    content: Optional[str] = None  # Only include if requested
    file_name: str
    file_size: int
    mime_type: str
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    chunk_count: int = 0
    is_processed: bool = False
    processing_status: str = "pending"
    processing_error: Optional[str] = None
    relevance_score: Optional[float] = None
    quality_score: Optional[float] = None
    entities: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    uploaded_by: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    content: str
    chunk_index: int
    word_count: int
    sentence_count: Optional[int] = None
    section_title: Optional[str] = None
    section_type: Optional[str] = None
    coherence_score: Optional[float] = None
    importance_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    document_type: Optional[str] = Field(None, description="Filter by document type")
    category: Optional[str] = Field(None, description="Filter by category")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results")


class DocumentSearchResult(BaseModel):
    document: DocumentResponse
    relevance_score: float
    excerpt: str
    chunk_index: int


class DocumentSearchResponse(BaseModel):
    query: str
    results: List[DocumentSearchResult]
    total_results: int


class DocumentUploadResponse(BaseModel):
    document_id: int
    title: str
    processing_status: str
    chunk_count: int
    message: str


class DocumentCollectionBase(BaseModel):
    name: str
    description: Optional[str] = None
    collection_type: Optional[str] = None
    is_active: bool = True
    is_public: bool = True


class DocumentCollectionCreate(DocumentCollectionBase):
    created_by: int


class DocumentCollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    collection_type: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class DocumentCollectionResponse(DocumentCollectionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    document_count: Optional[int] = 0

    class Config:
        from_attributes = True


class DocumentStatsResponse(BaseModel):
    total_documents: int
    processed_documents: int
    processing_rate: float
    by_type: Dict[str, int]
    by_category: Dict[str, int]
