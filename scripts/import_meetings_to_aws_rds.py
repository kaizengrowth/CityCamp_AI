#!/usr/bin/env python3
"""
Script to import meetings to AWS RDS
Supports importing from:
- Local PostgreSQL database
- CSV files
- JSON files
- PDF files (meeting minutes)
- Direct scraping from Tulsa government website

Usage:
    python import_meetings_to_aws_rds.py --source local_db --aws-db-url "postgresql://username:password@rds-endpoint:5432/dbname"
    python import_meetings_to_aws_rds.py --source csv --file meetings.csv --aws-db-url "postgresql://..."
    python import_meetings_to_aws_rds.py --source json --file meetings.json --aws-db-url "postgresql://..."
    python import_meetings_to_aws_rds.py --source pdf_dir --directory ./meeting_pdfs --aws-db-url "postgresql://..."
    python import_meetings_to_aws_rds.py --source scrape --aws-db-url "postgresql://..."
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import pdfplumber
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.meeting import Meeting, AgendaItem, MeetingCategory
from app.scrapers.tgov_scraper import TGOVScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('meeting_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MeetingImporter:
    """Main class for importing meetings to AWS RDS"""

    def __init__(self, aws_db_url: str, local_db_url: Optional[str] = None):
        self.aws_db_url = aws_db_url
        self.local_db_url = local_db_url or "postgresql://user:password@localhost:5435/citycamp_db"

        # Create AWS RDS connection
        try:
            self.aws_engine = create_engine(
                aws_db_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "connect_timeout": 30,
                    "application_name": "meeting_importer"
                }
            )
            self.aws_session = sessionmaker(autocommit=False, autoflush=False, bind=self.aws_engine)
            logger.info("Connected to AWS RDS successfully")
        except Exception as e:
            logger.error(f"Failed to connect to AWS RDS: {e}")
            raise

        # Create local DB connection if needed
        if local_db_url:
            try:
                self.local_engine = create_engine(local_db_url)
                self.local_session = sessionmaker(autocommit=False, autoflush=False, bind=self.local_engine)
                logger.info("Connected to local database successfully")
            except Exception as e:
                logger.warning(f"Failed to connect to local database: {e}")
                self.local_engine = None
                self.local_session = None

    def create_tables_if_not_exist(self):
        """Create database tables in AWS RDS if they don't exist"""
        try:
            logger.info("Creating tables in AWS RDS if they don't exist...")
            Base.metadata.create_all(bind=self.aws_engine)
            logger.info("Tables created/verified successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

    def test_connection(self):
        """Test the AWS RDS connection"""
        try:
            with self.aws_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("AWS RDS connection test successful")
                return True
        except Exception as e:
            logger.error(f"AWS RDS connection test failed: {e}")
            return False

    def import_from_local_db(self) -> int:
        """Import meetings from local PostgreSQL database to AWS RDS"""
        if not self.local_session:
            raise ValueError("Local database connection not available")

        imported_count = 0

        try:
            # Get local session
            local_db = self.local_session()
            aws_db = self.aws_session()

            # Get all meetings from local database
            local_meetings = local_db.query(Meeting).all()
            logger.info(f"Found {len(local_meetings)} meetings in local database")

            for local_meeting in local_meetings:
                try:
                    # Check if meeting already exists in AWS RDS
                    existing = aws_db.query(Meeting).filter(
                        Meeting.external_id == local_meeting.external_id
                    ).first()

                    if existing:
                        logger.debug(f"Meeting {local_meeting.external_id} already exists, skipping")
                        continue

                    # Create new meeting object for AWS RDS
                    aws_meeting = Meeting(
                        title=local_meeting.title,
                        description=local_meeting.description,
                        meeting_type=local_meeting.meeting_type,
                        meeting_date=local_meeting.meeting_date,
                        location=local_meeting.location,
                        meeting_url=local_meeting.meeting_url,
                        agenda_url=local_meeting.agenda_url,
                        minutes_url=local_meeting.minutes_url,
                        status=local_meeting.status,
                        external_id=local_meeting.external_id,
                        source=local_meeting.source,
                        topics=local_meeting.topics,
                        keywords=local_meeting.keywords,
                        summary=local_meeting.summary
                    )

                    aws_db.add(aws_meeting)
                    aws_db.flush()  # Get the ID

                    # Import agenda items
                    local_agenda_items = local_db.query(AgendaItem).filter(
                        AgendaItem.meeting_id == local_meeting.id
                    ).all()

                    for local_item in local_agenda_items:
                        aws_item = AgendaItem(
                            meeting_id=aws_meeting.id,
                            item_number=local_item.item_number,
                            title=local_item.title,
                            description=local_item.description,
                            item_type=local_item.item_type,
                            category=local_item.category,
                            keywords=local_item.keywords,
                            summary=local_item.summary,
                            impact_assessment=local_item.impact_assessment,
                            vote_required=local_item.vote_required,
                            vote_result=local_item.vote_result,
                            vote_details=local_item.vote_details,
                            attachments=local_item.attachments
                        )
                        aws_db.add(aws_item)

                    imported_count += 1

                    if imported_count % 10 == 0:
                        aws_db.commit()
                        logger.info(f"Imported {imported_count} meetings so far...")

                except Exception as e:
                    logger.error(f"Failed to import meeting {local_meeting.external_id}: {e}")
                    aws_db.rollback()
                    continue

            # Final commit
            aws_db.commit()
            logger.info(f"Successfully imported {imported_count} meetings from local database")

        except Exception as e:
            logger.error(f"Failed to import from local database: {e}")
            raise
        finally:
            if 'local_db' in locals():
                local_db.close()
            if 'aws_db' in locals():
                aws_db.close()

        return imported_count

    def import_from_csv(self, csv_file: str) -> int:
        """Import meetings from CSV file"""
        imported_count = 0

        try:
            aws_db = self.aws_session()

            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Parse meeting date
                        meeting_date = datetime.fromisoformat(row['meeting_date'])

                        # Check if meeting already exists
                        external_id = row.get('external_id') or f"csv-{row['title']}-{meeting_date.isoformat()}"
                        existing = aws_db.query(Meeting).filter(
                            Meeting.external_id == external_id
                        ).first()

                        if existing:
                            continue

                        # Create meeting
                        meeting = Meeting(
                            title=row['title'],
                            description=row.get('description'),
                            meeting_type=row.get('meeting_type', 'city_council'),
                            meeting_date=meeting_date,
                            location=row.get('location'),
                            meeting_url=row.get('meeting_url'),
                            agenda_url=row.get('agenda_url'),
                            minutes_url=row.get('minutes_url'),
                            status=row.get('status', 'completed'),
                            external_id=external_id,
                            source='csv_import',
                            topics=json.loads(row.get('topics', '[]')),
                            keywords=json.loads(row.get('keywords', '[]')),
                            summary=row.get('summary')
                        )

                        aws_db.add(meeting)
                        imported_count += 1

                        if imported_count % 10 == 0:
                            aws_db.commit()
                            logger.info(f"Imported {imported_count} meetings from CSV...")

                    except Exception as e:
                        logger.error(f"Failed to import CSV row: {e}")
                        continue

                aws_db.commit()
                logger.info(f"Successfully imported {imported_count} meetings from CSV")

        except Exception as e:
            logger.error(f"Failed to import from CSV: {e}")
            raise
        finally:
            if 'aws_db' in locals():
                aws_db.close()

        return imported_count

    def import_from_json(self, json_file: str) -> int:
        """Import meetings from JSON file"""
        imported_count = 0

        try:
            aws_db = self.aws_session()

            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

                meetings_data = data if isinstance(data, list) else data.get('meetings', [])

                for meeting_data in meetings_data:
                    try:
                        # Parse meeting date
                        meeting_date = datetime.fromisoformat(meeting_data['meeting_date'])

                        # Check if meeting already exists
                        external_id = meeting_data.get('external_id') or f"json-{meeting_data['title']}-{meeting_date.isoformat()}"
                        existing = aws_db.query(Meeting).filter(
                            Meeting.external_id == external_id
                        ).first()

                        if existing:
                            continue

                        # Create meeting
                        meeting = Meeting(
                            title=meeting_data['title'],
                            description=meeting_data.get('description'),
                            meeting_type=meeting_data.get('meeting_type', 'city_council'),
                            meeting_date=meeting_date,
                            location=meeting_data.get('location'),
                            meeting_url=meeting_data.get('meeting_url'),
                            agenda_url=meeting_data.get('agenda_url'),
                            minutes_url=meeting_data.get('minutes_url'),
                            status=meeting_data.get('status', 'completed'),
                            external_id=external_id,
                            source='json_import',
                            topics=meeting_data.get('topics', []),
                            keywords=meeting_data.get('keywords', []),
                            summary=meeting_data.get('summary')
                        )

                        aws_db.add(meeting)
                        aws_db.flush()

                        # Import agenda items if present
                        for item_data in meeting_data.get('agenda_items', []):
                            agenda_item = AgendaItem(
                                meeting_id=meeting.id,
                                item_number=item_data.get('item_number'),
                                title=item_data['title'],
                                description=item_data.get('description'),
                                item_type=item_data.get('item_type'),
                                category=item_data.get('category'),
                                keywords=item_data.get('keywords', []),
                                summary=item_data.get('summary'),
                                vote_required=item_data.get('vote_required', False),
                                vote_result=item_data.get('vote_result'),
                                attachments=item_data.get('attachments', [])
                            )
                            aws_db.add(agenda_item)

                        imported_count += 1

                        if imported_count % 10 == 0:
                            aws_db.commit()
                            logger.info(f"Imported {imported_count} meetings from JSON...")

                    except Exception as e:
                        logger.error(f"Failed to import JSON meeting: {e}")
                        continue

                aws_db.commit()
                logger.info(f"Successfully imported {imported_count} meetings from JSON")

        except Exception as e:
            logger.error(f"Failed to import from JSON: {e}")
            raise
        finally:
            if 'aws_db' in locals():
                aws_db.close()

        return imported_count

    def parse_pdf_filename(self, filename: str) -> Optional[Dict]:
        """Parse meeting information from PDF filename"""
        name = filename.replace('.pdf', '')

        # Extract date and time
        date_pattern = r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2})(PM|AM)?'
        date_match = re.search(date_pattern, name)

        if not date_match:
            special_date_pattern = r'(\d{4}-\d{2}-\d{2})'
            special_match = re.search(special_date_pattern, name)
            if special_match and "Special" in name:
                year, month, day = special_match.group(1).split('-')
                hour = 14  # Default special meetings to 2 PM
            else:
                logger.warning(f"Could not parse date from filename: {filename}")
                return None
        else:
            year, month, day = date_match.group(1).split('-')
            hour = int(date_match.group(2))
            ampm = date_match.group(3)

            if ampm:
                if ampm.upper() == 'PM' and hour != 12:
                    hour += 12
                elif ampm.upper() == 'AM' and hour == 12:
                    hour = 0

        meeting_type = "special_meeting" if "Special" in name else "city_council"
        meeting_date = datetime(int(year), int(month), int(day), hour, 0)
        external_id = f"tulsa-pdf-{year}-{month}-{day}-{hour:02d}00"

        if "Special" in name:
            title = f"Tulsa City Council Special Meeting - {meeting_date.strftime('%B %d, %Y')}"
        else:
            title = f"Tulsa City Council Meeting - {meeting_date.strftime('%B %d, %Y at %I:%M %p')}"

        return {
            "title": title,
            "meeting_date": meeting_date,
            "meeting_type": meeting_type,
            "external_id": external_id,
            "source": "pdf_import",
            "status": "completed",
            "location": "One Technology Center, Tulsa, OK",
            "filename": filename
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
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
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""

    def import_from_pdf_directory(self, pdf_directory: str) -> int:
        """Import meetings from PDF files in a directory"""
        imported_count = 0
        pdf_dir = Path(pdf_directory)

        if not pdf_dir.exists():
            raise ValueError(f"PDF directory does not exist: {pdf_directory}")

        try:
            aws_db = self.aws_session()

            pdf_files = list(pdf_dir.glob("*.pdf"))
            logger.info(f"Found {len(pdf_files)} PDF files to process")

            for pdf_file in pdf_files:
                try:
                    # Parse filename
                    meeting_info = self.parse_pdf_filename(pdf_file.name)
                    if not meeting_info:
                        continue

                    # Check if meeting already exists
                    existing = aws_db.query(Meeting).filter(
                        Meeting.external_id == meeting_info['external_id']
                    ).first()

                    if existing:
                        logger.debug(f"Meeting {meeting_info['external_id']} already exists, skipping")
                        continue

                    # Extract text from PDF
                    pdf_text = self.extract_text_from_pdf(str(pdf_file))

                    # Create meeting
                    meeting = Meeting(
                        title=meeting_info['title'],
                        description=f"Meeting minutes imported from {pdf_file.name}",
                        meeting_type=meeting_info['meeting_type'],
                        meeting_date=meeting_info['meeting_date'],
                        location=meeting_info['location'],
                        status=meeting_info['status'],
                        external_id=meeting_info['external_id'],
                        source=meeting_info['source'],
                        summary=pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text
                    )

                    aws_db.add(meeting)
                    imported_count += 1

                    if imported_count % 5 == 0:
                        aws_db.commit()
                        logger.info(f"Imported {imported_count} meetings from PDFs...")

                except Exception as e:
                    logger.error(f"Failed to import PDF {pdf_file.name}: {e}")
                    continue

            aws_db.commit()
            logger.info(f"Successfully imported {imported_count} meetings from PDF directory")

        except Exception as e:
            logger.error(f"Failed to import from PDF directory: {e}")
            raise
        finally:
            if 'aws_db' in locals():
                aws_db.close()

        return imported_count

    async def import_from_scraping(self, days_ahead: int = 30) -> int:
        """Import meetings by scraping Tulsa government website"""
        imported_count = 0

        try:
            aws_db = self.aws_session()
            scraper = TGOVScraper(aws_db)

            # Scrape upcoming meetings
            meetings = await scraper.scrape_upcoming_meetings(days_ahead)
            logger.info(f"Scraped {len(meetings)} meetings from Tulsa government website")

            for meeting in meetings:
                try:
                    # Scrape agenda items
                    await scraper.scrape_agenda_items(meeting)

                    # Scrape meeting minutes if available
                    if meeting.status == "completed":
                        await scraper.scrape_meeting_minutes(meeting)

                    imported_count += 1

                except Exception as e:
                    logger.error(f"Failed to process scraped meeting {meeting.external_id}: {e}")
                    continue

            aws_db.commit()
            logger.info(f"Successfully imported {imported_count} meetings from scraping")

        except Exception as e:
            logger.error(f"Failed to import from scraping: {e}")
            raise
        finally:
            if 'aws_db' in locals():
                aws_db.close()

        return imported_count

    def get_import_stats(self) -> Dict[str, int]:
        """Get statistics about imported meetings"""
        try:
            aws_db = self.aws_session()

            stats = {
                "total_meetings": aws_db.query(Meeting).count(),
                "total_agenda_items": aws_db.query(AgendaItem).count(),
                "meetings_by_type": {},
                "meetings_by_status": {},
                "meetings_by_source": {}
            }

            # Group by meeting type
            for meeting_type, count in aws_db.query(Meeting.meeting_type, Meeting.id).all():
                stats["meetings_by_type"][meeting_type] = stats["meetings_by_type"].get(meeting_type, 0) + 1

            # Group by status
            for status, count in aws_db.query(Meeting.status, Meeting.id).all():
                stats["meetings_by_status"][status] = stats["meetings_by_status"].get(status, 0) + 1

            # Group by source
            for source, count in aws_db.query(Meeting.source, Meeting.id).all():
                stats["meetings_by_source"][source] = stats["meetings_by_source"].get(source, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Failed to get import stats: {e}")
            return {}
        finally:
            if 'aws_db' in locals():
                aws_db.close()


def main():
    parser = argparse.ArgumentParser(description="Import meetings to AWS RDS")
    parser.add_argument("--aws-db-url", required=True, help="AWS RDS database URL")
    parser.add_argument("--local-db-url", help="Local database URL (for local_db source)")
    parser.add_argument("--source", required=True,
                       choices=["local_db", "csv", "json", "pdf_dir", "scrape"],
                       help="Data source to import from")
    parser.add_argument("--file", help="File path (for csv/json sources)")
    parser.add_argument("--directory", help="Directory path (for pdf_dir source)")
    parser.add_argument("--days-ahead", type=int, default=30,
                       help="Days ahead to scrape (for scrape source)")
    parser.add_argument("--create-tables", action="store_true",
                       help="Create database tables if they don't exist")
    parser.add_argument("--test-connection", action="store_true",
                       help="Test AWS RDS connection and exit")
    parser.add_argument("--stats", action="store_true",
                       help="Show import statistics and exit")

    args = parser.parse_args()

    # Initialize importer
    importer = MeetingImporter(args.aws_db_url, args.local_db_url)

    # Test connection if requested
    if args.test_connection:
        if importer.test_connection():
            logger.info("AWS RDS connection test successful")
            sys.exit(0)
        else:
            logger.error("AWS RDS connection test failed")
            sys.exit(1)

    # Create tables if requested
    if args.create_tables:
        importer.create_tables_if_not_exist()

    # Show stats if requested
    if args.stats:
        stats = importer.get_import_stats()
        logger.info("Import Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        sys.exit(0)

    # Import data based on source
    imported_count = 0

    try:
        if args.source == "local_db":
            imported_count = importer.import_from_local_db()
        elif args.source == "csv":
            if not args.file:
                logger.error("--file is required for CSV source")
                sys.exit(1)
            imported_count = importer.import_from_csv(args.file)
        elif args.source == "json":
            if not args.file:
                logger.error("--file is required for JSON source")
                sys.exit(1)
            imported_count = importer.import_from_json(args.file)
        elif args.source == "pdf_dir":
            if not args.directory:
                logger.error("--directory is required for PDF directory source")
                sys.exit(1)
            imported_count = importer.import_from_pdf_directory(args.directory)
        elif args.source == "scrape":
            import asyncio
            imported_count = asyncio.run(importer.import_from_scraping(args.days_ahead))

        logger.info(f"Import completed successfully. Imported {imported_count} meetings.")

        # Show final stats
        stats = importer.get_import_stats()
        logger.info("Final Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
