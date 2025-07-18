#!/usr/bin/env python3
"""
Script to extract actual minutes content from PDF files and update meeting summaries
"""

import os
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
from app.core.database import get_db
from app.models.meeting import Meeting
from sqlalchemy.orm import Session


def extract_minutes_content(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text_content = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
            return text_content.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def parse_meeting_date_from_filename(filename: str) -> datetime:
    """Parse meeting date from filename"""
    # Pattern: 22-1018-1_22-1018-1 2022-10-19 5PM Minutes.pdf
    date_pattern = r"(\d{4}-\d{2}-\d{2})"
    match = re.search(date_pattern, filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%Y-%m-%d")
    return None


def update_meeting_minutes(db: Session, pdf_folder: str):
    """Update meeting summaries with actual minutes content"""
    pdf_folder_path = Path(pdf_folder)

    if not pdf_folder_path.exists():
        print(f"PDF folder not found: {pdf_folder}")
        return

    # Get all PDF files
    pdf_files = list(pdf_folder_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    updated_count = 0

    for pdf_file in pdf_files:
        try:
            # Parse date from filename
            meeting_date = parse_meeting_date_from_filename(pdf_file.name)
            if not meeting_date:
                print(f"Could not parse date from filename: {pdf_file.name}")
                continue

            # Find matching meeting in database by comparing date parts only
            from datetime import date

            meeting_date_only = meeting_date.date()

            # Get all meetings and filter by date
            all_meetings = (
                db.query(Meeting).filter(Meeting.source == "imported_minutes").all()
            )
            matching_meeting = None

            for meeting in all_meetings:
                if (
                    meeting.meeting_date
                    and meeting.meeting_date.date() == meeting_date_only
                ):
                    matching_meeting = meeting
                    break

            if not matching_meeting:
                print(
                    f"No meeting found for date {meeting_date_only} from file {pdf_file.name}"
                )
                continue

            # Extract minutes content
            minutes_content = extract_minutes_content(str(pdf_file))
            if not minutes_content:
                print(f"No content extracted from {pdf_file.name}")
                continue

            # Update meeting summary with actual minutes content
            matching_meeting.summary = minutes_content
            db.commit()

            print(
                f"Updated meeting {matching_meeting.id} ({matching_meeting.title}) with {len(minutes_content)} characters of minutes content"
            )
            updated_count += 1

        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
            db.rollback()

    print(f"Successfully updated {updated_count} meetings with minutes content")


def main():
    """Main function"""
    # Path to the PDF folder (adjust as needed)
    pdf_folder = "/Users/kailin/Desktop/CityCamp_AI/tests/downloaded_documents"

    db = next(get_db())
    try:
        update_meeting_minutes(db, pdf_folder)
    finally:
        db.close()


if __name__ == "__main__":
    main()
