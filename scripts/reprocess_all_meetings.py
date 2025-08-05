#!/usr/bin/env python3
"""
Reprocess all meeting PDFs with proper AI summaries and fix PDF storage.

This script:
1. Removes meetings with placeholder summaries
2. Reprocesses all PDFs with proper AI categorization
3. Sets up proper PDF storage
4. Updates the database with correct paths
5. Generates comprehensive AI summaries for each meeting
"""

import os
import sys
import re
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.database import SessionLocal, engine, Base
from app.models.meeting import Meeting, AgendaItem, MeetingCategory
from app.services.ai_categorization_service import AICategorization
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

# Configuration
DOCUMENTS_FOLDER = Path(__file__).parent.parent / "tests" / "downloaded_documents"
PDF_STORAGE_FOLDER = Path(__file__).parent.parent / "backend" / "storage" / "pdfs"

def parse_filename(filename: str) -> Tuple[Optional[str], Optional[datetime], Optional[str]]:
    """
    Parse meeting PDF filename to extract metadata.

    Example filename: "22-1017-1_22-1017-1 2022-10-19 4PM Minutes.pdf"
    Returns: (meeting_id, meeting_date, meeting_type)
    """
    try:
        # Remove .pdf extension
        name = filename.replace('.pdf', '')

        # Extract meeting ID - flexible format (e.g., "22-1017-1", "24-522-1", "23-78-1")
        meeting_id_match = re.search(r'(\d{2}-\d{2,4}-\d+)', name)
        meeting_id = meeting_id_match.group(1) if meeting_id_match else None

        # Extract date (e.g., "2022-10-19")
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', name)
        meeting_date = None
        if date_match:
            meeting_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')

        # Extract meeting type (4PM, 5PM, Special Meeting, etc.)
        type_match = re.search(r'(\d+PM|Special Meeting)', name)
        meeting_type = type_match.group(1) if type_match else "Regular Meeting"

        return meeting_id, meeting_date, meeting_type

    except Exception as e:
        print(f"Error parsing filename {filename}: {e}")
        return None, None, None

def setup_storage_directory():
    """Set up the PDF storage directory"""
    try:
        PDF_STORAGE_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"✅ Storage directory created: {PDF_STORAGE_FOLDER}")
        return True
    except Exception as e:
        print(f"❌ Error creating storage directory: {e}")
        return False

def store_pdf_file(pdf_path: Path, meeting_id: str) -> str:
    """Store PDF file in the storage folder and return the stored path"""
    try:
        # Generate storage filename
        storage_filename = f"{meeting_id}.pdf"
        storage_path = PDF_STORAGE_FOLDER / storage_filename

        # Copy PDF file to storage
        shutil.copy2(pdf_path, storage_path)

        # Return relative path for database storage
        return f"storage/pdfs/{storage_filename}"

    except Exception as e:
        print(f"Error storing PDF file: {e}")
        return ""

def clear_placeholder_meetings(db: Session):
    """Remove meetings with placeholder summaries"""
    try:
        placeholder_meetings = db.query(Meeting).filter(
            Meeting.summary.like("Minutes imported from PDF%")
        ).all()

        print(f"🗑️  Found {len(placeholder_meetings)} meetings with placeholder summaries")

        for meeting in placeholder_meetings:
            # Delete related agenda items first
            db.query(AgendaItem).filter(AgendaItem.meeting_id == meeting.id).delete()
            # Delete the meeting
            db.delete(meeting)

        db.commit()
        print(f"✅ Cleared {len(placeholder_meetings)} placeholder meetings")

    except Exception as e:
        print(f"❌ Error clearing placeholder meetings: {e}")
        db.rollback()

def process_pdf_file(pdf_path: Path, ai_service: AICategorization, db: Session) -> bool:
    """Process a single PDF file with comprehensive AI analysis"""
    try:
        print(f"\n📄 Processing: {pdf_path.name}")

        # Parse filename for metadata
        meeting_id, meeting_date, meeting_type = parse_filename(pdf_path.name)

        if not meeting_id or not meeting_date:
            print(f"  ⚠️  Could not parse metadata from filename: {pdf_path.name}")
            return False

        # Check if meeting already exists - use upsert logic
        existing_meeting = db.query(Meeting).filter(
            Meeting.external_id == meeting_id
        ).first()

        is_update = existing_meeting is not None
        if is_update:
            print(f"  🔄 Meeting {meeting_id} exists, updating with enhanced AI...")
        else:
            print(f"  ➕ Creating new meeting {meeting_id}...")

        # Read PDF content
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        # Process with AI
        print(f"  🤖 Processing with AI...")
        processed_content = ai_service.process_meeting_minutes(
            pdf_content, meeting_id, db
        )

        # Store PDF file
        pdf_storage_path = store_pdf_file(pdf_path, meeting_id)

        if not pdf_storage_path:
            print(f"  ❌ Failed to store PDF file")
            return False

        # Create or update meeting record with enhanced AI data
        if is_update:
            # Update existing meeting with enhanced AI analysis
            meeting = existing_meeting
            meeting.description = processed_content.summary[:500] if processed_content.summary else meeting.description
            meeting.topics = processed_content.categories
            meeting.keywords = processed_content.keywords
            meeting.summary = processed_content.summary
            meeting.detailed_summary = processed_content.detailed_summary
            meeting.voting_records = [vote.__dict__ for vote in processed_content.voting_records]
            meeting.vote_statistics = processed_content.vote_statistics
            if pdf_storage_path:  # Only update if new PDF was stored successfully
                meeting.minutes_url = pdf_storage_path

            # Clear existing agenda items for this meeting
            db.query(AgendaItem).filter(AgendaItem.meeting_id == meeting.id).delete()
            print(f"  🔄 Updated existing meeting and cleared old agenda items")
        else:
            # Create new meeting record
            meeting = Meeting(
                title=f"{meeting_type} - {meeting_date.strftime('%B %d, %Y')}",
                description=processed_content.summary[:500] if processed_content.summary else "City Council Meeting",
                meeting_type=meeting_type,
                meeting_date=meeting_date,
                location="City Hall",
                external_id=meeting_id,
                source="tulsa_city_council_pdf",
                topics=processed_content.categories,
                keywords=processed_content.keywords,
                summary=processed_content.summary,
                detailed_summary=processed_content.detailed_summary,
                voting_records=[vote.__dict__ for vote in processed_content.voting_records],
                vote_statistics=processed_content.vote_statistics,
                minutes_url=pdf_storage_path,
                status="completed"
            )
            db.add(meeting)
            print(f"  ➕ Created new meeting record")

        db.flush()  # Get the meeting ID

        # Create agenda items
        for i, item_data in enumerate(processed_content.agenda_items):
            agenda_item = AgendaItem(
                meeting_id=meeting.id,
                item_number=str(i + 1),
                title=item_data['title'],
                description=item_data['description'],
                category=processed_content.categories[0] if processed_content.categories else None,
                keywords=processed_content.keywords,
                summary=item_data['description'][:500]  # Limit summary length
            )
            db.add(agenda_item)

        db.commit()

        action = "Updated" if is_update else "Created"
        print(f"  ✅ {action} meeting {meeting_id}")
        print(f"     📊 Categories: {', '.join(processed_content.categories)}")
        print(f"     🏷️  Keywords: {', '.join(processed_content.keywords[:5])}")
        print(f"     📝 Agenda items: {len(processed_content.agenda_items)}")
        print(f"     🗳️  Voting records: {len(processed_content.voting_records)}")
        print(f"     📈 Vote statistics: {processed_content.vote_statistics}")
        print(f"     📄 PDF stored: {pdf_storage_path}")

        return True

    except Exception as e:
        print(f"  ❌ Error processing {pdf_path.name}: {e}")
        db.rollback()
        return False

def main():
    """Main function to reprocess all meetings"""
    parser = argparse.ArgumentParser(description="Reprocess all meetings with enhanced AI categorization")
    parser.add_argument("--aws-db-url", help="AWS RDS database URL (optional - uses local DB if not provided)")

    args = parser.parse_args()

    print("🚀 Starting comprehensive meeting reprocessing...")

    # Check if documents folder exists
    if not DOCUMENTS_FOLDER.exists():
        print(f"❌ Documents folder not found: {DOCUMENTS_FOLDER}")
        return

    # Set up storage directory
    if not setup_storage_directory():
        return

    # Initialize database connection
    if args.aws_db_url:
        print(f"📡 Connecting to AWS RDS database...")
        aws_engine = create_engine(args.aws_db_url)
        AWSSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=aws_engine)
        db = AWSSessionLocal()
    else:
        print(f"🏠 Using local database...")
        db = SessionLocal()

    try:
        # Initialize AI service
        ai_service = AICategorization()

        # Initialize categories in database
        try:
            ai_service.initialize_categories_in_db(db)
        except Exception as e:
            print(f"Error initializing categories: {e}")

        # Clear placeholder meetings
        clear_placeholder_meetings(db)

        # Get all PDF files
        pdf_files = list(DOCUMENTS_FOLDER.glob("*.pdf"))
        print(f"📁 Found {len(pdf_files)} PDF files to process")

        # Process each PDF
        success_count = 0
        total_count = len(pdf_files)

        for pdf_file in pdf_files:
            if process_pdf_file(pdf_file, ai_service, db):
                success_count += 1

        print(f"\n🎉 Reprocessing complete!")
        print(f"📊 Successfully processed: {success_count}/{total_count} meetings")

        # Show statistics
        total_meetings = db.query(Meeting).count()
        meetings_with_ai_summaries = db.query(Meeting).filter(
            ~Meeting.summary.like("Minutes imported from PDF%")
        ).count()

        print(f"📈 Total meetings in database: {total_meetings}")
        print(f"🤖 Meetings with AI summaries: {meetings_with_ai_summaries}")
        print(f"💾 PDF storage directory: {PDF_STORAGE_FOLDER}")

    except Exception as e:
        print(f"❌ Error during reprocessing: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
