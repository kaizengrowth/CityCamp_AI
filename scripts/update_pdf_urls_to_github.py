#!/usr/bin/env python3
"""
Update PDF URLs to GitHub Raw URLs
This script updates all meeting PDF URLs to point to GitHub raw URLs.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from app.core.database import SessionLocal
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_pdf_urls_to_github():
    """Update all meeting PDF URLs to use GitHub raw URLs."""
    db = SessionLocal()

    try:
        # Update all meetings to use correct GitHub raw URLs for PDFs
        result = db.execute(text("""
            UPDATE meetings
            SET minutes_url = CASE
                WHEN external_id IS NOT NULL AND external_id != '' THEN
                    'https://raw.githubusercontent.com/kaizengrowth/CityCamp_AI/main/tests/downloaded_documents/' ||
                    external_id || '_' || external_id || ' ' ||
                    TO_CHAR(meeting_date, 'YYYY-MM-DD') || ' ' ||
                    CASE
                        WHEN meeting_type LIKE '%4PM%' THEN '4PM Minutes.pdf'
                        WHEN meeting_type LIKE '%5PM%' THEN '5PM Minutes.pdf'
                        ELSE meeting_type || ' Minutes.pdf'
                    END
                ELSE minutes_url
            END
            WHERE external_id IS NOT NULL AND external_id != ''
        """))

        logger.info(f"Updated {result.rowcount} meetings with GitHub PDF URLs")
        db.commit()

        # Show a few examples
        result = db.execute(text("SELECT id, title, external_id, minutes_url FROM meetings WHERE minutes_url LIKE '%github%' LIMIT 3;"))
        logger.info("Example updated URLs:")
        for row in result:
            logger.info(f"  Meeting {row[0]}: {row[1][:50]}...")
            logger.info(f"    External ID: {row[2]}")
            logger.info(f"    PDF URL: {row[3]}")
            logger.info("")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_pdf_urls_to_github()
