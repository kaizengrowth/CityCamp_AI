# CityCamp AI Documentation

Welcome to the CityCamp AI documentation. This directory contains all project documentation organized by topic.

The Tulsa Archive Scraper system can scrape all historical documents (2020-2025) from the official City of Tulsa Council Archive, supporting 16 different meeting types including Regular Council, committees, and task forces. See [TULSA_ARCHIVE_SCRAPER_README.md](TULSA_ARCHIVE_SCRAPER_README.md) for complete details.

## Documentation Index

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup for local development

### Setup & Configuration
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Environment variables and .env files guide

### Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

### Data Collection & Scraping
- **[TULSA_ARCHIVE_SCRAPER_README.md](TULSA_ARCHIVE_SCRAPER_README.md)** - Historical document scraping system

### System Information
- **[RAG_SYSTEM_README.md](RAG_SYSTEM_README.md)** - Retrieval Augmented Generation system
- **[SECURITY_SETUP.md](SECURITY_SETUP.md)** - Security configuration
- **[TWILIO_SETUP.md](TWILIO_SETUP.md)** - SMS notification setup
- **[GEOJSON_DISTRICT_BOUNDARIES.md](GEOJSON_DISTRICT_BOUNDARIES.md)** - District mapping data

## Project Structure

```
CityCamp_AI/
├── docs/                  # All documentation (you are here!)
│   ├── README.md          # This file - documentation index
│   ├── QUICKSTART.md      # Quick setup guide
│   ├── ENVIRONMENT_SETUP.md # Environment configuration
│   ├── TROUBLESHOOTING.md # Common issues and solutions
│   └── screenshots/       # Application screenshots
├── backend/              # FastAPI backend application
├── frontend/             # React frontend application
├── scripts/              # Utility scripts for development and deployment
└── tests/               # Test files and documentation
```

## Core System Features

### Backend (FastAPI + SQLAlchemy + PostgreSQL)
- **RESTful API** - Complete CRUD operations for all resources
- **Authentication** - JWT-based user authentication and authorization
- **Database** - PostgreSQL with Alembic migrations
- **AI Integration** - OpenAI GPT-4 for document processing and chatbot
- **Document Processing** - PDF parsing and text extraction
- **Web Scraping** - Automated meeting data collection

### Frontend (React + TypeScript + Tailwind CSS)
- **Modern UI** - Responsive design with Tailwind CSS
- **Real-time Updates** - Live data updates for meetings and campaigns
- **Interactive Maps** - District boundaries and representative mapping
- **Document Viewer** - In-browser PDF viewing and highlighting

### AI & Natural Language Processing
- **Chatbot** - GPT-4 powered conversational interface
- **RAG System** - Retrieval-Augmented Generation for document queries
- **Content Categorization** - Automatic topic classification
- **Semantic Search** - Vector-based document similarity search

## Quick Navigation

- **Need to get started quickly?** → [QUICKSTART.md](QUICKSTART.md)
- **Setting up environment variables?** → [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **Running into issues?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Working with scrapers?** → [TULSA_ARCHIVE_SCRAPER_README.md](TULSA_ARCHIVE_SCRAPER_README.md)
- **Setting up RAG system?** → [RAG_SYSTEM_README.md](RAG_SYSTEM_README.md)

## Support

For additional help or questions:
1. Check the relevant documentation files above
2. Review the troubleshooting guide
3. Check the GitHub issues and discussions

---

**Note**: This documentation is kept up-to-date with the latest system features and configuration requirements.
