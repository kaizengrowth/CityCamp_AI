#!/usr/bin/env python3
"""
Update Meeting Image Paths Script
Updates the database with image paths after PDF-to-image conversion
"""

import os
import sys
import argparse
from pathlib import Path
import logging
import re
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / "backend" / ".env")

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.meeting import Meeting

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_meeting_info_from_path(image_path: Path) -> tuple[datetime, str, str]:
    """Extract meeting date, time, and identifier from image path"""
    # Path format: YYYY/MM/DD/meeting_folder_name/image_files
    parts = image_path.parts
    if len(parts) >= 4:
        try:
            year, month, day = parts[-4], parts[-3], parts[-2]
            meeting_date = datetime(int(year), int(month), int(day))
            folder_name = parts[-1]

            # Extract time from folder name (4PM, 5PM, Special, etc.)
            time_match = re.search(r'(\d+PM|Special)', folder_name, re.IGNORECASE)
            meeting_time = time_match.group(1) if time_match else "Unknown"

            return meeting_date, meeting_time, folder_name
        except (ValueError, IndexError):
            pass

    return None, None, None


def find_matching_meeting(db: SessionLocal, meeting_date: datetime, meeting_time: str) -> Meeting:
    """Find a meeting in the database that matches the date and time"""
    try:
        # Query meetings for the specific date
        meetings = db.query(Meeting).filter(
            Meeting.meeting_date >= meeting_date,
            Meeting.meeting_date < meeting_date.replace(hour=23, minute=59, second=59)
        ).all()

        if not meetings:
            return None

        # If only one meeting on this date, return it
        if len(meetings) == 1:
            return meetings[0]

        # Try to match by time in title or minutes_url
        for meeting in meetings:
            title_lower = meeting.title.lower() if meeting.title else ""
            url_lower = meeting.minutes_url.lower() if meeting.minutes_url else ""
            time_lower = meeting_time.lower()

            if (time_lower in title_lower or
                time_lower in url_lower or
                (time_lower == "special" and "special" in title_lower)):
                return meeting

        # Fallback: return the first meeting
        logger.warning(f"Multiple meetings found for {meeting_date.date()}, using first one")
        return meetings[0]

    except Exception as e:
        logger.error(f"Error finding matching meeting: {e}")
        return None


def update_meeting_image_paths(dry_run: bool = True):
    """Update database with image paths from the organized storage directory"""

    images_base_dir = Path("backend/storage/meeting-images")

    if not images_base_dir.exists():
        logger.error(f"Images directory does not exist: {images_base_dir}")
        return

    db = SessionLocal()

    try:
        # Find all meeting image directories
        meeting_folders = []
        for date_dir in images_base_dir.rglob("*"):
            if date_dir.is_dir() and any(date_dir.glob("*.png")):
                meeting_folders.append(date_dir)

        logger.info(f"Found {len(meeting_folders)} meeting folders with images")

        updated_count = 0
        matched_count = 0

        for folder in meeting_folders:
            # Extract meeting info from path
            meeting_date, meeting_time, folder_name = extract_meeting_info_from_path(folder)

            if not meeting_date:
                logger.warning(f"Could not extract date from path: {folder}")
                continue

            # Find matching meeting in database
            meeting = find_matching_meeting(db, meeting_date, meeting_time)

            if not meeting:
                logger.warning(f"No matching meeting found for {meeting_date.date()} {meeting_time}")
                continue

            matched_count += 1

            # Get all image files in this folder
            image_files = sorted(folder.glob("*.png"))
            if not image_files:
                continue

            # Create relative paths from the images base directory
            relative_paths = []
            for image_file in image_files:
                relative_path = str(image_file.relative_to(images_base_dir))
                relative_paths.append(relative_path)

            logger.info(f"Meeting {meeting.id} ({meeting_date.date()} {meeting_time}): {len(relative_paths)} images")

            if not dry_run:
                # Update the meeting with image paths
                meeting.image_paths = relative_paths
                updated_count += 1

        if not dry_run:
            db.commit()
            logger.info(f"✅ Updated {updated_count} meetings with image paths")
        else:
            logger.info(f"🔍 Dry run: Would update {matched_count} meetings with image paths")

        logger.info(f"📊 Summary: {matched_count} meetings matched, {len(meeting_folders)} image folders found")

    except Exception as e:
        logger.error(f"Error updating image paths: {e}")
        if not dry_run:
            db.rollback()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Update meeting image paths in database")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    update_meeting_image_paths(dry_run=not args.apply)


if __name__ == "__main__":
    main()
