#!/usr/bin/env python3
"""
Script to import Tulsa City Council meeting minutes PDFs into the database
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import pdfplumber
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.meeting import Meeting

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost:5435/citycamp_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_filename(filename: str) -> Optional[Dict]:
    """
    Parse meeting information from filename
    Format: YY-XXX-Z_YY-XXX-Z YYYY-MM-DD HH:MM Minutes.pdf
    """
    # Remove .pdf extension
    name = filename.replace('.pdf', '')

    # Extract the date and time part - fixed pattern
    date_pattern = r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2})(PM|AM)?'
    date_match = re.search(date_pattern, name)

    if not date_match:
        # Try pattern for special meetings without time
        special_date_pattern = r'(\d{4}-\d{2}-\d{2})'
        special_match = re.search(special_date_pattern, name)
        if special_match and "Special" in name:
            year, month, day = special_match.group(1).split('-')
            # Default special meetings to 2 PM
            hour = 14
            ampm = None
        else:
            print(f"Could not parse date from filename: {filename}")
            return None
    else:
        year, month, day = date_match.group(1).split('-')
        hour = int(date_match.group(2))
        ampm = date_match.group(3)

    # Convert to 24-hour format
    if ampm:
        if ampm.upper() == 'PM' and hour != 12:
            hour += 12
        elif ampm.upper() == 'AM' and hour == 12:
            hour = 0

    # Extract meeting type from filename
    meeting_type = "city_council"
    if "Special" in name:
        meeting_type = "special_meeting"

    # Create meeting date
    meeting_date = datetime(int(year), int(month), int(day), hour, 0)  # Default to 0 minutes

    # Generate external ID
    external_id = f"tulsa-{year}-{month}-{day}-{hour:02d}00"

    # Create title
    if "Special" in name:
        title = f"Tulsa City Council Special Meeting - {meeting_date.strftime('%B %d, %Y')}"
    else:
        title = f"Tulsa City Council Meeting - {meeting_date.strftime('%B %d, %Y at %I:%M %p')}"

    return {
        "title": title,
        "meeting_date": meeting_date,
        "meeting_type": meeting_type,
        "external_id": external_id,
        "source": "imported_minutes",
        "status": "completed",
        "location": "One Technology Center, Tulsa, OK",
        "filename": filename
    }

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def create_or_update_meeting(session, meeting_data: Dict, pdf_path: str) -> Meeting:
    """Create or update meeting in database"""
    # Check if meeting already exists
    existing_meeting = session.query(Meeting).filter(
        Meeting.external_id == meeting_data["external_id"]
    ).first()

    if existing_meeting:
        print(f"Updating existing meeting: {meeting_data['title']}")
        # Update existing meeting
        existing_meeting.title = meeting_data["title"]
        existing_meeting.meeting_date = meeting_data["meeting_date"]
        existing_meeting.meeting_type = meeting_data["meeting_type"]
        existing_meeting.status = meeting_data["status"]
        existing_meeting.location = meeting_data["location"]
        meeting = existing_meeting
    else:
        print(f"Creating new meeting: {meeting_data['title']}")
        # Create new meeting
        meeting = Meeting(
            external_id=meeting_data["external_id"],
            title=meeting_data["title"],
            meeting_date=meeting_data["meeting_date"],
            meeting_type=meeting_data["meeting_type"],
            source=meeting_data["source"],
            status=meeting_data["status"],
            location=meeting_data["location"]
        )
        session.add(meeting)

    # Extract text from PDF and store as description
    minutes_text = extract_text_from_pdf(pdf_path)
    if minutes_text:
        # Store the minutes text in the description field
        # Truncate if too long (PostgreSQL Text field can handle large content)
        if len(minutes_text) > 10000:  # Limit to first 10k characters for display
            meeting.description = minutes_text[:10000] + "\n\n[Content truncated - full minutes available in PDF]"
        else:
            meeting.description = minutes_text

        # Store the PDF filename in the summary field for reference
        meeting.summary = f"Minutes imported from PDF: {meeting_data['filename']}"

    session.commit()
    session.refresh(meeting)
    return meeting

def main():
    """Main function to process all PDF files"""
    # Path to the downloaded documents
    docs_path = Path(__file__).parent.parent / "tests" / "downloaded_documents"

    if not docs_path.exists():
        print(f"Documents directory not found: {docs_path}")
        return

    # Create database session
    session = SessionLocal()

    try:
        # Process all PDF files
        pdf_files = list(docs_path.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files to process")

        processed_count = 0
        error_count = 0

        for pdf_file in sorted(pdf_files):
            try:
                print(f"\nProcessing: {pdf_file.name}")

                # Parse meeting information from filename
                meeting_data = parse_filename(pdf_file.name)
                if not meeting_data:
                    error_count += 1
                    continue

                # Create or update meeting in database
                meeting = create_or_update_meeting(session, meeting_data, str(pdf_file))
                processed_count += 1

                print(f"✓ Successfully processed: {meeting.title}")

            except Exception as e:
                print(f"✗ Error processing {pdf_file.name}: {e}")
                error_count += 1

        print(f"\n=== Import Summary ===")
        print(f"Total files: {len(pdf_files)}")
        print(f"Successfully processed: {processed_count}")
        print(f"Errors: {error_count}")

    except Exception as e:
        print(f"Error during import: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
