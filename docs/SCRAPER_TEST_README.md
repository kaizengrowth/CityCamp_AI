# CityCamp AI Scraper Testing Guide

This guide shows you how to test the scraper functionality locally to see if it can generate meeting minutes and agenda items.

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
  - Attempts to scrape minutes (for past meetings)
  - Shows preview of found content

### 2. Test Meeting Scraper (Full Workflow)
- Runs the complete scraping pipeline
- Shows statistics: meetings found, agenda items created, minutes scraped
- Stores results in a local SQLite database

### 3. Test Specific URL
- Allows you to test scraping a specific meeting URL
- Useful for debugging specific meetings

### 4. Show Database Contents
- Displays all meetings and agenda items found
- Shows which meetings have minutes available

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
     Minutes found: 15432 characters
     Preview: TULSA CITY COUNCIL MEETING MINUTES January 15, 2024...
```

## Troubleshooting

### No Meetings Found
- Check if tulsacouncil.org is accessible
- The website structure may have changed
- Check the scraper selectors in `app/scrapers/tgov_scraper.py`

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

The scraper is designed to work with your existing tgov_scraper_api code:

- **TGOVScraper**: Adapts your scraping logic to CityCamp AI models
- **MeetingScraper**: Orchestrates the complete workflow
- **Database Integration**: Stores results in CityCamp AI database schema

## Next Steps

Once the scraper is working locally:

1. **Deploy to production**: The scraper endpoints are available at `/api/v1/scraper/`
2. **Schedule regular runs**: Use the admin endpoints to run scraping cycles
3. **Monitor results**: Check the database for scraped meetings and minutes
4. **Integrate notifications**: Users will be notified of new meetings

## Files Involved

- `test_scraper.py`: This test script
- `app/scrapers/tgov_scraper.py`: Core scraping logic
- `app/scrapers/meeting_scraper.py`: Workflow orchestration
- `app/api/v1/endpoints/scraper.py`: API endpoints
- `app/models/meeting.py`: Database models
