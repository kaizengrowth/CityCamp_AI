#!/usr/bin/env python3
"""
Migration script to update existing meeting image paths from local API URLs to GitHub raw URLs.
This script should be run once to migrate existing data after the code changes.
"""

import sys
import os
from pathlib import Path
from sqlalchemy import cast, String

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from app.core.database import SessionLocal
from app.models.meeting import Meeting
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_image_paths_to_github(dry_run: bool = True):
    """Migrate existing meeting image paths from local API URLs to GitHub raw URLs."""
    github_raw_base = "https://raw.githubusercontent.com/kaizengrowth/CityCamp_AI/main"
    db = SessionLocal()

    try:
        # Find all meetings with image paths that are not empty
        # Use cast to text for comparison to avoid JSON operator issues
        meetings = db.query(Meeting).filter(
            Meeting.image_paths.isnot(None),
            cast(Meeting.image_paths, String) != '[]'
        ).all()

        logger.info(f"Found {len(meetings)} meetings with image paths")

        updated_count = 0
        for meeting in meetings:
            if meeting.image_paths and len(meeting.image_paths) > 0:
                # Check if already GitHub URLs
                first_path = meeting.image_paths[0]
                if first_path.startswith("https://raw.githubusercontent.com/"):
                    logger.info(f"Meeting {meeting.id}: Already has GitHub URLs, skipping")
                    continue

                # Convert local API paths to GitHub URLs
                github_urls = []
                for path in meeting.image_paths:
                    if path.startswith("/api/v1/meeting-images/"):
                        # Remove the API prefix and convert to GitHub raw URL
                        relative_path = path.replace("/api/v1/meeting-images/", "")
                        github_url = f"{github_raw_base}/backend/storage/meeting-images/{relative_path}"
                        github_urls.append(github_url)
                    else:
                        # Keep other URLs as-is
                        github_urls.append(path)

                logger.info(f"Meeting {meeting.id}: Converting {len(meeting.image_paths)} paths to GitHub URLs")

                if not dry_run:
                    meeting.image_paths = github_urls
                    updated_count += 1

        if not dry_run:
            db.commit()
            logger.info(f"Successfully updated {updated_count} meetings")
        else:
            logger.info(f"DRY RUN: Would update {len([m for m in meetings if m.image_paths and len(m.image_paths) > 0 and not m.image_paths[0].startswith('https://raw.githubusercontent.com/')])} meetings")

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate meeting image paths to GitHub URLs")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Run in dry-run mode (default: True)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform the migration (overrides --dry-run)")

    args = parser.parse_args()

    # If --execute is specified, turn off dry-run
    dry_run = not args.execute if args.execute else args.dry_run

    logger.info(f"Starting migration {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    migrate_image_paths_to_github(dry_run=dry_run)
