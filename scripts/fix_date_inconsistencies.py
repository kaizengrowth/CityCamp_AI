#!/usr/bin/env python3
"""
Fix Date Inconsistencies
Identify and fix date inconsistencies between meeting titles and meeting_date fields
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.meeting import Meeting
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_date_from_title(title: str) -> tuple[datetime, str]:
    """Extract date from meeting title and return standardized format"""

    # Common date patterns in titles
    patterns = [
        r"(\w+\s+\d{1,2},\s+\d{4})",  # "November 06, 2024"
        r"(\d{1,2}/\d{1,2}/\d{4})",   # "11/06/2024"
        r"(\d{4}-\d{2}-\d{2})",       # "2024-11-06"
        r"(\w{3}\s+\d{1,2},\s+\d{4})", # "Nov 06, 2024"
    ]

    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            date_str = match.group(1)

            # Try to parse the date
            formats = [
                "%B %d, %Y",    # November 06, 2024
                "%b %d, %Y",    # Nov 06, 2024
                "%m/%d/%Y",     # 11/06/2024
                "%Y-%m-%d",     # 2024-11-06
            ]

            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date, date_str
                except ValueError:
                    continue

    return None, None


def fix_date_inconsistencies(dry_run: bool = True):
    """Fix date inconsistencies in meeting records"""

    print("🔍 Analyzing Date Inconsistencies")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Get all meetings
        meetings = db.query(Meeting).all()

        inconsistencies = []
        fixed_count = 0

        for meeting in meetings:
            if not meeting.title or not meeting.meeting_date:
                continue

            # Extract date from title
            title_date, title_date_str = extract_date_from_title(meeting.title)

            if not title_date:
                continue

            # Compare with meeting_date (ignore time for comparison)
            db_date = meeting.meeting_date.replace(hour=0, minute=0, second=0, microsecond=0)
            title_date = title_date.replace(hour=0, minute=0, second=0, microsecond=0)

            if db_date != title_date:
                inconsistency = {
                    'id': meeting.id,
                    'title': meeting.title,
                    'db_date': meeting.meeting_date,
                    'title_date': title_date,
                    'title_date_str': title_date_str,
                    'difference_days': abs((db_date - title_date).days)
                }
                inconsistencies.append(inconsistency)

        print(f"📊 Found {len(inconsistencies)} date inconsistencies")

        if not inconsistencies:
            print("✅ No date inconsistencies found!")
            return

        # Sort by difference in days (most significant first)
        inconsistencies.sort(key=lambda x: x['difference_days'], reverse=True)

        print(f"\n📋 Top inconsistencies:")
        for i, inc in enumerate(inconsistencies[:10], 1):
            print(f"{i:2d}. Meeting #{inc['id']}: {inc['title'][:60]}...")
            print(f"     DB Date:    {inc['db_date'].strftime('%Y-%m-%d %H:%M')}")
            print(f"     Title Date: {inc['title_date'].strftime('%Y-%m-%d')} ({inc['title_date_str']})")
            print(f"     Difference: {inc['difference_days']} days")
            print()

        if dry_run:
            print("🔍 DRY RUN MODE - No changes made")
            print("Run with --fix to apply corrections")
        else:
            print("🔧 Applying fixes...")

            for inc in inconsistencies:
                meeting = db.query(Meeting).get(inc['id'])
                if meeting:
                    # Update the meeting_date to match the title
                    # Keep the original time if it was set
                    original_time = meeting.meeting_date.time()
                    new_date = inc['title_date'].replace(
                        hour=original_time.hour,
                        minute=original_time.minute,
                        second=original_time.second
                    )

                    print(f"   Fixing Meeting #{inc['id']}: {inc['db_date']} → {new_date}")
                    meeting.meeting_date = new_date
                    fixed_count += 1

            db.commit()
            print(f"✅ Fixed {fixed_count} date inconsistencies")

        # Additional analysis
        print(f"\n📈 Analysis Summary:")
        print(f"   Total meetings analyzed: {len(meetings)}")
        print(f"   Meetings with inconsistencies: {len(inconsistencies)}")
        print(f"   Average difference: {sum(inc['difference_days'] for inc in inconsistencies) / len(inconsistencies):.1f} days")

        # Group by difference magnitude
        small_diffs = [inc for inc in inconsistencies if inc['difference_days'] <= 1]
        large_diffs = [inc for inc in inconsistencies if inc['difference_days'] > 1]

        print(f"   Small differences (≤1 day): {len(small_diffs)}")
        print(f"   Large differences (>1 day): {len(large_diffs)}")

    except Exception as e:
        logger.error(f"Error fixing date inconsistencies: {str(e)}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix date inconsistencies in meeting records")
    parser.add_argument("--fix", action="store_true", help="Apply fixes (default is dry run)")

    args = parser.parse_args()

    fix_date_inconsistencies(dry_run=not args.fix)
