#!/usr/bin/env python3
"""
Sync Production Database to Local Development Database
This script copies all meetings from production to local database.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from app.core.database import SessionLocal, engine
from app.models.meeting import Meeting, AgendaItem, MeetingCategory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Production database URL
PROD_DATABASE_URL = "postgresql://citycamp_user:CityCampSecure2024%21@citycamp-ai-db.c8lywk6yg0um.us-east-1.rds.amazonaws.com:5432/citycamp_db"

# Local database URL
LOCAL_DATABASE_URL = "postgresql://user:password@localhost:5435/citycamp_db"


def sync_production_to_local(dry_run: bool = True):
    """Sync production database to local database."""

    # Create production database connection
    prod_engine = create_engine(PROD_DATABASE_URL)
    ProdSession = sessionmaker(bind=prod_engine)

    # Use local database connection
    local_engine = create_engine(LOCAL_DATABASE_URL)
    LocalSession = sessionmaker(bind=local_engine)

    prod_db = ProdSession()
    local_db = LocalSession()

    try:
        # Get production meetings count
        prod_count = prod_db.query(Meeting).count()
        local_count = local_db.query(Meeting).count()

        logger.info(f"Production database: {prod_count} meetings")
        logger.info(f"Local database: {local_count} meetings")

        if not dry_run:
            # Clear local meetings first
            logger.info("Clearing local meetings...")
            local_db.query(AgendaItem).delete()
            local_db.query(Meeting).delete()
            local_db.commit()

            # Copy all meetings from production
            logger.info("Copying meetings from production...")
            prod_meetings = prod_db.query(Meeting).all()

            for i, meeting in enumerate(prod_meetings):
                # Create new meeting object for local database
                new_meeting = Meeting(
                    title=meeting.title,
                    description=meeting.description,
                    meeting_type=meeting.meeting_type,
                    meeting_date=meeting.meeting_date,
                    location=meeting.location,
                    meeting_url=meeting.meeting_url,
                    agenda_url=meeting.agenda_url,
                    minutes_url=meeting.minutes_url,
                    status=meeting.status,
                    external_id=meeting.external_id,
                    source=meeting.source,
                    document_type=meeting.document_type,
                    topics=meeting.topics,
                    keywords=meeting.keywords,
                    summary=meeting.summary,
                    detailed_summary=meeting.detailed_summary,
                    voting_records=meeting.voting_records,
                    vote_statistics=meeting.vote_statistics,
                    image_paths=meeting.image_paths,
                    created_at=meeting.created_at,
                    updated_at=meeting.updated_at
                )

                local_db.add(new_meeting)

                if (i + 1) % 50 == 0:
                    logger.info(f"Copied {i + 1}/{prod_count} meetings...")
                    local_db.commit()

            local_db.commit()
            logger.info(f"✅ Successfully synced {prod_count} meetings to local database")

            # Verify sync
            final_local_count = local_db.query(Meeting).count()
            with_images = local_db.query(Meeting).filter(
                Meeting.image_paths.isnot(None)
            ).filter(
                Meeting.image_paths != []
            ).count()

            logger.info(f"Local database now has {final_local_count} meetings")
            logger.info(f"Meetings with images: {with_images}")

        else:
            logger.info("🔍 Dry run complete. Use --execute to perform the sync.")

    except Exception as e:
        logger.error(f"Error during sync: {e}")
        local_db.rollback()
        raise
    finally:
        prod_db.close()
        local_db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync production database to local")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Run in dry-run mode (default: True)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform the sync (overrides --dry-run)")

    args = parser.parse_args()

    # If --execute is specified, turn off dry-run
    dry_run = not args.execute if args.execute else args.dry_run

    logger.info(f"Starting sync {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    sync_production_to_local(dry_run=dry_run)
