#!/usr/bin/env python3
"""
Process a folder of meeting minutes PDFs with enhanced AI and upsert into DB.

Usage:
  python scripts/process_minutes_folder.py --folder PATH --apply

Defaults:
  --folder ../tests/new_downloaded_documents

This script:
  - Ensures `meetings.key_decisions` column exists
  - Copies PDFs into backend/storage/pdfs/
  - Runs GPT-5 enhanced extraction (150–250 word summary, filtered keywords)
  - Upserts Meeting + AgendaItems with vote statistics for UI
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure backend is importable when running from project root or backend dir
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# App imports
from app.core.database import SessionLocal, engine  # type: ignore
from app.services.ai_categorization_service import AICategorization  # type: ignore
from app.services.ai_categorization_service_gpt5 import AICategorizationGPT5  # type: ignore
from app.services.meeting_upsert_service import MeetingUpsertService  # type: ignore
from sqlalchemy import text  # type: ignore

STORAGE_DIR = BACKEND_DIR / "storage" / "pdfs"


def parse_filename_metadata(filename: str) -> tuple[str, Optional[datetime], Optional[str]]:
    """Extract external_id, meeting_date, and time_label from filename.
    Expected pattern: '25-214-1_25-214-1 2025-03-05 4PM Minutes.pdf'
    """
    name = Path(filename).stem
    # external id: take token before first space
    parts = name.split(" ")
    external_id = parts[0]

    # date and time
    date_match = re.search(r"(20\d{2}-\d{2}-\d{2})", name)
    time_match = re.search(r"(\d{1,2})(AM|PM)", name)
    meeting_date: Optional[datetime] = None
    time_label: Optional[str] = None
    if date_match:
        date_str = date_match.group(1)
        if time_match:
            hour = int(time_match.group(1)) % 12
            if time_match.group(2) == "PM":
                hour += 12
            meeting_date = datetime.strptime(f"{date_str} {hour:02d}:00", "%Y-%m-%d %H:%M")
            time_label = f"{time_match.group(1)}{time_match.group(2)}"
        else:
            meeting_date = datetime.strptime(date_str, "%Y-%m-%d")
    return external_id, meeting_date, time_label


def ensure_key_decisions_column() -> None:
    """Add meetings.key_decisions if it doesn't exist (safe idempotent)."""
    with engine.connect() as conn:  # type: ignore
        conn.execute(
            text(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='meetings' AND column_name='key_decisions'
                    ) THEN
                        ALTER TABLE meetings ADD COLUMN key_decisions JSON NULL;
                    END IF;
                END$$;
                """
            )
        )
        conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Process meeting minutes folder with enhanced AI")
    parser.add_argument("--folder", type=str, default=str(PROJECT_ROOT / "tests" / "new_downloaded_documents"))
    parser.add_argument("--apply", action="store_true", help="Apply DB updates (default: dry run)")
    parser.add_argument("--use-gpt5", action="store_true", help="Use experimental GPT-5 categorizer (does not affect existing service)")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.exists():
        print(f"❌ Folder not found: {folder}")
        sys.exit(1)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure schema
    ensure_key_decisions_column()

    db = SessionLocal()
    ai = AICategorizationGPT5() if args.use_gpt5 else AICategorization()

    pdf_files = sorted(folder.glob("*.pdf"))
    print(f"📁 Found {len(pdf_files)} PDFs in {folder}")

    processed = 0
    created = 0
    updated = 0
    errors = 0

    try:
        for pdf_path in pdf_files:
            try:
                external_id, meeting_date, time_label = parse_filename_metadata(pdf_path.name)
                # Copy into backend storage for serving from API
                stored_name = pdf_path.name
                dest_path = STORAGE_DIR / stored_name
                if not dest_path.exists():
                    shutil.copy2(pdf_path, dest_path)
                minutes_url = f"storage/pdfs/{stored_name}"

                # Read bytes
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                # GPT-5 processing
                content = ai.process_meeting_minutes(pdf_bytes, 0, db)

                # Build meeting metadata
                title = f"City Council Meeting Minutes {meeting_date.date() if meeting_date else ''} {time_label or ''}".strip()
                meeting_metadata = {
                    "title": title or pdf_path.stem,
                    "description": None,
                    "meeting_type": "city_council",
                    "meeting_date": meeting_date or datetime.utcnow(),
                    "location": "One Technology Center, Tulsa, OK",
                    "source": "imported_minutes",
                    "status": "completed",
                }

                meeting, is_new = MeetingUpsertService.upsert_meeting(
                    db=db,
                    external_id=external_id,
                    processed_content=content,
                    meeting_metadata=meeting_metadata,
                    pdf_storage_path=minutes_url,
                )

                if args.apply:
                    db.commit()
                else:
                    db.rollback()

                processed += 1
                created += 1 if is_new else 0
                updated += 0 if is_new else 1
                print(f"✅ {'Created' if is_new else 'Updated'} meeting {external_id} -> {minutes_url}")

            except Exception as e:
                db.rollback()
                errors += 1
                print(f"❌ Error processing {pdf_path.name}: {e}")
                continue

    finally:
        db.close()

    print("\n📊 Results")
    print(f"Processed: {processed}")
    print(f"Created:   {created}")
    print(f"Updated:   {updated}")
    print(f"Errors:    {errors}")


if __name__ == "__main__":
    main()
