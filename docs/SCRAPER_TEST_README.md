# CityCamp AI Scraper Testing Guide

This guide shows you how to test the scraper functionality locally to see if it can discover meetings and agenda items. **Note**: Meeting minutes require a two-step process (see Meeting Minutes section below).

## Quick Start

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies (if not already done):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the test script:**
   ```bash
   python test_scraper.py
   ```

## What the Test Does

The test script provides several options:

### 1. Test TGOV Scraper (Direct)
- Tests the core scraping functionality
- Attempts to scrape upcoming meetings from tulsacouncil.org
- For each meeting found:
  - Scrapes agenda items
  - **For minutes**: Identifies PDF links but does NOT extract content (see Meeting Minutes section)
  - Shows preview of found content

### 2. Test Meeting Scraper (Full Workflow)
- Runs the complete scraping pipeline
- Shows statistics: meetings found, agenda items created, PDF links identified
- Stores results in a local SQLite database

### 3. Test Specific URL
- Allows you to test scraping a specific meeting URL
- Useful for debugging specific meetings

### 4. Show Database Contents
- Displays all meetings and agenda items found
- Shows which meetings have PDF links available

## Meeting Minutes: Two-Step Process

**Important**: The scraper workflow for meeting minutes involves two separate steps:

### Step 1: Live Scraping (BeautifulSoup)
- **What it does**: Discovers meetings and identifies PDF links
- **Technology**: BeautifulSoup for HTML parsing
- **Output**: Stores PDF URLs like "PDF minutes available at: [URL]"
- **Does NOT**: Extract actual PDF text content

### Step 2: PDF Import (pdfplumber)
- **What it does**: Extracts full text content from downloaded PDFs
- **Technology**: pdfplumber for PDF text extraction
- **Script**: `scripts/import_meeting_minutes.py`
- **Input**: PDF files in `tests/downloaded_documents/`
- **Output**: Full meeting minutes text stored in database

### Running PDF Import
```bash
# After PDFs are downloaded to tests/downloaded_documents/
python scripts/import_meeting_minutes.py
```

## Expected Output

When working correctly, you should see output like:

```
TESTING TGOV SCRAPER
==================================================
1. Testing upcoming meetings scrape...
   Found 3 meetings
   - City Council Meeting on 2024-01-15 19:00:00
     Testing agenda items for: City Council Meeting
     Found 8 agenda items
     Testing minutes for: City Council Meeting
     Minutes found: PDF minutes available at: https://example.com/minutes.pdf
```

**Note**: The scraper identifies PDF links but doesn't extract content. Use the import script for full text extraction.

## Troubleshooting

### No Meetings Found
- Check if tulsacouncil.org is accessible
- The website structure may have changed
- Check the scraper selectors in `app/scrapers/tgov_scraper.py`

### Minutes Show Only URLs
- This is expected behavior - the live scraper only identifies PDF links
- To extract content, download PDFs and run `scripts/import_meeting_minutes.py`

### Import Errors
- Make sure you're in the backend directory
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Database Errors
- The script uses SQLite for testing (no PostgreSQL needed)
- Delete `test_scraper.db` if you encounter database issues

### Network Issues
- Ensure you have internet connectivity
- Some corporate firewalls may block scraping

## Customizing the Test

You can modify the test script to:

1. **Change the target website:**
   Edit `base_url` in `TGOVScraper.__init__()`

2. **Test different date ranges:**
   Modify `days_ahead` parameter in the test functions

3. **Add debug output:**
   Change logging level to `DEBUG` in the script

4. **Test specific URLs:**
   Replace the `test_url` in `test_specific_url()` function

## Integration with Your Existing Scripts

The scraper system uses a two-tier approach:

- **TGOVScraper**: Discovers meetings and PDF links using BeautifulSoup
- **MeetingScraper**: Orchestrates the live scraping workflow
- **import_meeting_minutes.py**: Extracts text from downloaded PDFs using pdfplumber
- **Database Integration**: Stores results in CityCamp AI database schema

## Next Steps

Once the scraper is working locally:

1. **Deploy to production**: The scraper endpoints are available at `/api/v1/scraper/`
2. **Schedule regular runs**: Use the admin endpoints to run scraping cycles
3. **Set up PDF import**: Configure automated PDF download and text extraction
4. **Monitor results**: Check the database for scraped meetings and extracted minutes
5. **Integrate notifications**: Users will be notified of new meetings

## Files Involved

### Live Scraping (BeautifulSoup)
- `test_scraper.py`: This test script
- `app/scrapers/tgov_scraper.py`: Core scraping logic
- `app/scrapers/meeting_scraper.py`: Workflow orchestration
- `app/api/v1/endpoints/scraper.py`: API endpoints

### PDF Import (pdfplumber)
- `backend/extract_minutes_content.py`: Alternative PDF processor

### Data Models
- `app/models/meeting.py`: Database models
