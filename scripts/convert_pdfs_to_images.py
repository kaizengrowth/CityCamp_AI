#!/usr/bin/env python3
"""
PDF to Images Conversion Script
Converts meeting PDF documents to high-quality images organized by date
Independent of AI processing for efficiency and reusability
"""

import os
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
import logging

# PDF processing imports
import fitz  # PyMuPDF
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_date_from_filename(filename: str) -> tuple[datetime, str]:
    """Extract meeting date and type from PDF filename"""
    # Pattern: XX-XXX-X_XX-XXX-X YYYY-MM-DD [4PM|5PM|Special] Minutes.pdf
    patterns = [
        r'(\d{2}-\d{3}-\d+).*?(\d{4}-\d{2}-\d{2})\s+(\d+PM|Special).*?Minutes',
        r'(\d{2}-\d{3}-\d+).*?(\d{4}-\d{2}-\d{2})\s+(\d+\s*PM|Special).*?Minutes',
        r'.*?(\d{4}-\d{2}-\d{2}).*?(\d+PM|Special).*?Minutes'
    ]

    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            try:
                date_str = match.group(-2) if len(match.groups()) > 2 else match.group(1)
                meeting_type = match.group(-1)
                meeting_date = datetime.strptime(date_str, "%Y-%m-%d")
                return meeting_date, meeting_type
            except (ValueError, IndexError):
                continue

    # Fallback: try to extract just the date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        try:
            meeting_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            return meeting_date, "Regular"
        except ValueError:
            pass

    logger.warning(f"Could not extract date from filename: {filename}")
    return datetime.now(), "Unknown"


def create_safe_filename(text: str) -> str:
    """Create a safe filename from text"""
    # Replace spaces and special characters
    safe = re.sub(r'[^\w\-_\.]', '_', text)
    # Remove multiple underscores
    safe = re.sub(r'_+', '_', safe)
    return safe.strip('_')


def convert_pdf_to_images(pdf_path: Path, output_base_dir: Path, verbose: bool = False) -> bool:
    """Convert a single PDF to images organized by date"""
    try:
        if verbose:
            logger.info(f"Processing: {pdf_path}")

        # Extract meeting info from filename
        meeting_date, meeting_type = extract_date_from_filename(pdf_path.name)

        # Create directory structure: YYYY/MM/DD/meeting_folder_name/
        date_dir = output_base_dir / str(meeting_date.year) / f"{meeting_date.month:02d}" / f"{meeting_date.day:02d}"

        # Create meeting folder name from PDF filename
        pdf_stem = pdf_path.stem
        safe_folder_name = create_safe_filename(pdf_stem + f"_{meeting_type}")
        meeting_dir = date_dir / safe_folder_name
        meeting_dir.mkdir(parents=True, exist_ok=True)

        if verbose:
            logger.info(f"Output directory: {meeting_dir}")

        # Open PDF
        pdf_document = fitz.open(pdf_path)

        if verbose:
            logger.info(f"PDF has {len(pdf_document)} pages")

        # Convert each page to image
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)

            # Render page as image (2x zoom for better quality)
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            # Create filename: meeting_title_date_pageXX.png
            page_filename = f"{create_safe_filename(pdf_stem)}_{meeting_date.strftime('%Y_%m_%d')}_page{page_num+1:02d}.png"
            image_path = meeting_dir / page_filename

            # Save image
            image.save(image_path, "PNG", optimize=True)

            if verbose:
                logger.info(f"Saved page {page_num+1}: {image_path}")

        pdf_document.close()

        if verbose:
            logger.info(f"✅ Successfully converted {pdf_path.name} ({len(pdf_document)} pages)")

        return True

    except Exception as e:
        logger.error(f"❌ Error converting {pdf_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert PDF meeting documents to organized images")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", type=str, default="backend/storage/meeting-images",
                       help="Base output directory for images")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files to convert")
    logger.info(f"Output directory: {output_dir}")

    # Convert each PDF
    success_count = 0
    for pdf_file in pdf_files:
        if convert_pdf_to_images(pdf_file, output_dir, args.verbose):
            success_count += 1

    logger.info(f"✅ Conversion complete: {success_count}/{len(pdf_files)} files processed successfully")


if __name__ == "__main__":
    main()
