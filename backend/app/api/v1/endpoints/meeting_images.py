import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

# Base directory for meeting images
IMAGES_BASE_DIR = Path("backend/storage/meeting-images")


@router.get("/meeting-images/{image_path:path}")
async def get_meeting_image(image_path: str):
    """Serve meeting document images"""
    try:
        # Construct the full file path
        file_path = IMAGES_BASE_DIR / image_path

        # Security check: ensure the path is within our images directory
        if not str(file_path.resolve()).startswith(str(IMAGES_BASE_DIR.resolve())):
            raise HTTPException(status_code=403, detail="Access forbidden")

        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Image not found")

        # Return the image file
        return FileResponse(
            path=str(file_path), media_type="image/png", filename=file_path.name
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")
