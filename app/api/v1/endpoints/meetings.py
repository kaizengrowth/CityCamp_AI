import json
from pathlib import Path
from typing import List, Optional

import httpx
from app.core.database import get_db
from app.models.meeting import AgendaItem, Meeting, MeetingCategory
from app.schemas.meeting import (
    CategoryResponse,
    MeetingDetailResponse,
    MeetingListResponse,
)
from app.services.ai_categorization_service import AICategorization
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import Text, cast
from sqlalchemy.orm import Session
