# Tulsa City Council Archive Scraper

A comprehensive system for scraping, categorizing, and analyzing historical documents from the **official City of Tulsa Council Archive** at `https://www.cityoftulsa.org/apps/TulsaCouncilArchive`.

## 🎯 Overview

This system can automatically:
- **🕸️ Scrape ALL historical documents** from 2020-2025
- **🏷️ Categorize 16 different meeting types** (Regular Council, committees, task forces)
- **📥 Download PDF documents** and extract text content
- **🔍 Find embedded minutes** within Regular meeting agendas
- **🤖 Process with AI** for enhanced summaries and voting analysis
- **💾 Store in database** with comprehensive categorization

---

## 📋 Meeting Types Supported

### Main Council & Committees
- **🏛️ Regular Council** - Main city council meetings
- **💰 Budget and Special Projects Committee** - Financial planning and budgets
- **🚧 Public Works Committee** - Infrastructure and utilities
- **🏙️ Urban And Economic Development Committee** - Planning and growth

### Task Forces & Special Committees (12 additional types)
- **🌟 61st & Peoria Quality of Life Task Force**
- **🏗️ Capital Improvement Program Task Force**
- **🚊 Eastern Flyer Passenger Rail Task Force**
- **🏠 HUD Grant Fund Allocation Committee**
- **🍽️ Hunger and Food Taskforce Committee**
- **🤝 Mayor-Council Retreat**
- **🚔 Public Safety Task Force**
- **🌊 River Infrastructure Task Force**
- **💡 Street Lighting Task Force**
- **🏪 Food Desert Task Force**
- **🪶 Tribal Nations Relations Committee**
- **🎒 Truancy Prevention Task Force**

---

## 🛠️ Prerequisites

### Required Dependencies
```bash
# Backend dependencies (already in requirements.txt)
pip install requests beautifulsoup4 pdfplumber sqlalchemy psycopg2-binary

# AI processing (optional)
pip install openai
```

### Database Setup
1. **Database Migration**: Add required fields to meetings table
```bash
python scripts/add_document_type_migration.py --aws-db-url "your-database-url"
```

2. **Environment Variables**: Ensure OpenAI API key is configured (for AI processing)
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

---

## 🚀 Scripts Overview

### 1. Production Scraper (`scripts/run_comprehensive_tulsa_scraper.py`)

**Purpose**: Complete production-ready scraper for historical data collection

**Usage**:
```bash
# Dry run (recommended first)
python scripts/run_comprehensive_tulsa_scraper.py --dry-run

# Limited test run (10 documents)
python scripts/run_comprehensive_tulsa_scraper.py \
  --max-downloads 10 \
  --aws-db-url "postgresql://user:pass@host:5432/db"

# Full historical scrape (2020-2025, all meeting types)
python scripts/run_comprehensive_tulsa_scraper.py \
  --process-ai \
  --aws-db-url "postgresql://user:pass@host:5432/db"

# Specific meeting types only
python scripts/run_comprehensive_tulsa_scraper.py \
  --meeting-types "Regular" "Public Works Committee" \
  --start-year 2022 --end-year 2025 \
  --aws-db-url "postgresql://user:pass@host:5432/db"
```

**Arguments**:
- `--start-year`: Start year for scraping (default: 2020)
- `--end-year`: End year for scraping (default: 2025)
- `--meeting-types`: Specific meeting types (default: all 16 types)
- `--max-downloads`: Limit number of downloads (0 = no limit)
- `--process-ai`: Enable AI processing of documents
- `--aws-db-url`: Database connection string
- `--dry-run`: Test run without saving data

**Expected Output**:
```
🚀 COMPREHENSIVE TULSA ARCHIVE SCRAPER
============================================================
📅 Date Range: 2020 - 2025
🏷️ Meeting Types: All
💾 Database: AWS RDS
🤖 AI Processing: Enabled
============================================================

📡 PHASE 1: COMPREHENSIVE SCRAPING
--------------------------------------------------
✅ Found 847 meetings across all types and years

📋 Breakdown by meeting type:
  • regular_council: 234 meetings
  • budget_committee: 89 meetings
  • public_works_committee: 156 meetings
  • urban_economic_committee: 112 meetings
  • public_safety_task_force: 45 meetings
  [... additional meeting types ...]

📥 PHASE 2: DOCUMENT DOWNLOAD & DATABASE STORAGE
--------------------------------------------------
📋 Processing 847 meetings...
✅ Documents downloaded: 847
➕ Database records created: 623
🔄 Database records updated: 224

🤖 PHASE 3: AI PROCESSING
--------------------------------------------------
🤖 Processing 847 meetings with AI...
✅ AI processing completed: 847

🎉 COMPREHENSIVE SCRAPING COMPLETE!
============================================================
📊 FINAL RESULTS:
  • Historical range: 2020 - 2025
  • Meeting types scraped: 16
  • Total meetings found: 847
  • Documents downloaded: 847
  • Database records created: 623
  • Database records updated: 224
  • AI processing completed: 847
  • Errors encountered: 0
============================================================
🏆 Perfect run - no errors!
```

### 2. Test Scripts

#### Comprehensive Scraper Test (`scripts/test_comprehensive_scraper.py`)
**Purpose**: Test all scraper functionality without full data collection

```bash
python scripts/test_comprehensive_scraper.py --aws-db-url "your-db-url"
```

**Expected Output**:
```
🧪 Testing Comprehensive Tulsa Archive Scraper
======================================================================

🏷️ Test 1: Meeting Type Mapping
--------------------------------------------------
Total meeting types configured: 16
  • Regular → regular_council (Form Value: 0)
  • Budget and Special Projects Committee Meeting → budget_committee (Form Value: 257)
  [... all 16 meeting types listed ...]

🚀 Test 3: Limited Comprehensive Scraping
--------------------------------------------------
Testing with 3 meeting types for 2024-2025...
📊 Results: Total meetings found: 15

📥 Test 4: Document Download Test
--------------------------------------------------
✅ Downloaded: storage/pdfs/tulsa-archive-29982-agenda.pdf
✅ Extracted 5667 characters from PDF
🔍 Found 0 potential minutes links

🎉 Comprehensive Scraper Test Complete!
```

#### Debug Scripts
```bash
# Analyze website structure
python scripts/debug_tulsa_archive.py

# Comprehensive form analysis
python scripts/debug_tulsa_archive_comprehensive.py
```

### 3. Database Migration Script (`scripts/add_document_type_migration.py`)

**Purpose**: Add required database fields for document categorization

```bash
python scripts/add_document_type_migration.py --aws-db-url "your-db-url"
```

**Expected Output**:
```
🔄 Adding document_type field to meetings table...
✅ Added document_type column
✅ detailed_summary column already exists
✅ voting_records column already exists
✅ vote_statistics column already exists
✅ Updated document_type for 248 existing meetings

📋 Updated schema:
  - detailed_summary: text (NULL)
  - document_type: character varying (NULL)
  - vote_statistics: json (NULL)
  - voting_records: json (NULL)

🎉 Migration completed successfully!
```

---

## 📊 Expected Data Collection Results

### Typical Historical Scrape (2020-2025)
- **📋 Total Meetings**: 500-1500+ meetings (depending on activity)
- **📁 Document Types**:
  - Agendas: ~80-90% of documents
  - Minutes: ~10-20% (embedded in Regular meeting agendas)
- **🏷️ Meeting Distribution**:
  - Regular Council: ~200-300 meetings
  - Committee Meetings: ~150-250 each
  - Task Forces: ~20-100 each (varies by active periods)

### File Storage Structure
```
backend/storage/pdfs/
├── tulsa-archive-29981-agenda.pdf
├── tulsa-archive-29982-agenda.pdf
├── tulsa-archive-29982-minutes-1.pdf
├── tulsa-archive-29983-agenda.pdf
└── [hundreds more PDFs...]
```

### Database Records Created
```sql
-- Sample meeting record
{
  "id": 1234,
  "title": "Regular - August 06, 2025",
  "meeting_type": "regular_council",
  "document_type": "agenda",
  "meeting_date": "2025-08-06T21:00:00Z",
  "external_id": "tulsa-archive-29982",
  "source": "tulsa_archive",
  "agenda_url": "https://www.cityoftulsa.org/apps/COTDisplayDocument/?DocumentType=Agenda&DocumentIdentifiers=29982",
  "minutes_url": "storage/pdfs/tulsa-archive-29982-agenda.pdf",
  "topics": ["transportation", "budget", "public_safety"],
  "keywords": ["councilor", "ordinance", "motion", "approved"],
  "summary": "Council discussed transportation improvements and approved budget amendments.",
  "detailed_summary": "## Key Proceedings...",
  "voting_records": [
    {
      "item_description": "Budget Amendment 2025-08",
      "outcome": "passed",
      "vote_counts": {"yes": 7, "no": 1, "abstain": 0},
      "representatives": {"Councilor Smith": "yes", "Councilor Jones": "no"},
      "vote_type": "roll_call"
    }
  ],
  "vote_statistics": {"total_votes": 3, "passed": 2, "failed": 1}
}
```

---

## 🎛️ Frontend Integration

### Enhanced Filtering Options
The scraper populates the frontend with enhanced filtering capabilities:

**Document Type Filter**:
- All Documents
- 📋 Agendas
- 📝 Minutes

**Meeting Type Filter** (organized dropdown):
- **Main Council & Committees**
  - 🏛️ Regular Council
  - 💰 Budget Committee
  - 🚧 Public Works
  - 🏙️ Urban & Economic
- **Task Forces & Special Committees**
  - 🌟 61st & Peoria Quality of Life
  - 🏗️ Capital Improvement
  - [... 10 more task forces ...]

### Frontend Usage
```typescript
// Example filtered results
const filteredMeetings = meetings.filter(meeting => {
  const matchesDocumentType = documentTypeFilter === 'all' ||
                             meeting.document_type === documentTypeFilter;
  const matchesMeetingType = meetingTypeFilter === 'all' ||
                           meeting.meeting_type === meetingTypeFilter;
  return matchesDocumentType && matchesMeetingType;
});
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Test database connection
python -c "
import psycopg2
conn = psycopg2.connect('your-db-url')
print('✅ Database connection successful')
conn.close()
"
```

#### 2. PDF Download Failures
- Check internet connection
- Verify PDF URLs are accessible
- Look for rate limiting (scraper includes delays)

#### 3. AI Processing Errors
```bash
# Verify OpenAI API key
python -c "
import os
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
"
```

#### 4. Missing Meeting Types
If new meeting types appear on the website:
1. Run `debug_tulsa_archive_comprehensive.py` to see current options
2. Update `meeting_type_mapping` in `TulsaArchiveScraper`
3. Update frontend dropdown options

### Log Analysis
```bash
# Monitor scraping progress
tail -f logs/scraper.log

# Check for errors
grep "ERROR" logs/scraper.log
```

---

## 🎯 Performance Considerations

### Scraping Speed
- **Rate Limiting**: 0.5 second delay between requests (respectful)
- **Estimated Time**: 2-4 hours for full historical scrape (2020-2025)
- **Concurrent Processing**: Single-threaded to avoid overwhelming server

### Resource Usage
- **Disk Space**: ~500MB-2GB for full historical collection
- **Memory**: ~200-500MB during processing
- **Network**: ~100-500MB download depending on document sizes

### Optimization Tips
```bash
# Process specific years only
--start-year 2023 --end-year 2025

# Process specific meeting types
--meeting-types "Regular" "Public Works Committee"

# Limit downloads for testing
--max-downloads 50
```

---

## 📈 Monitoring and Maintenance

### Regular Maintenance Tasks
1. **Monthly Updates**: Run scraper monthly to get new documents
2. **Database Cleanup**: Monitor for duplicates (scraper prevents them)
3. **PDF Storage**: Archive older PDFs if disk space becomes an issue
4. **AI Reprocessing**: Reprocess documents if AI models improve

### Monitoring Commands
```bash
# Check database status
python -c "
from app.core.database import SessionLocal
from app.models.meeting import Meeting
db = SessionLocal()
count = db.query(Meeting).filter(Meeting.source == 'tulsa_archive').count()
print(f'Tulsa Archive meetings in database: {count}')
db.close()
"

# Check recent activity
python -c "
from app.core.database import SessionLocal
from app.models.meeting import Meeting
from datetime import datetime, timedelta
db = SessionLocal()
recent = db.query(Meeting).filter(
    Meeting.source == 'tulsa_archive',
    Meeting.created_at > datetime.now() - timedelta(days=30)
).count()
print(f'New meetings added in last 30 days: {recent}')
db.close()
"
```

---

## 🏆 Success Metrics

A successful comprehensive scrape should achieve:
- **📊 Coverage**: 500+ meetings across 6 years
- **🏷️ Categorization**: All 16 meeting types represented
- **📥 Download Rate**: >95% successful PDF downloads
- **🤖 AI Processing**: >90% successful AI analysis
- **💾 Database Storage**: All meetings properly categorized
- **❌ Error Rate**: <5% errors overall

---

## 🤝 Contributing

### Adding New Meeting Types
1. Update `meeting_type_mapping` in `TulsaArchiveScraper`
2. Add corresponding frontend option in `MeetingsPage.tsx`
3. Test with new meeting type
4. Update this documentation

### Improving AI Processing
1. Modify prompts in `ai_categorization_service.py`
2. Test with sample documents
3. Update expected output documentation

---

**🎉 The Tulsa Archive Scraper provides comprehensive access to the complete historical record of Tulsa City Council proceedings, with advanced categorization and AI-powered analysis capabilities!**
