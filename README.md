# CityCamp AI - Tulsa Civic Engagement Platform

A modern CivicTech application that connects Tulsa residents with their city government through automated notifications, AI-powered assistance, and community organizing tools.

## Features

### Core Functionality
- **Meeting Notifications**: Automated alerts for Tulsa City Council meetings and agendas
- **Topic Preferences**: Residents can select areas of interest for targeted notifications
- **AI Chatbot**: Interactive assistant for questions about Tulsa City government
- **Email Generation**: AI-powered tool to help residents contact their representatives
- **Community Platform**: Connect with other residents and organize campaigns

### Technical Features
- **Real-time Notifications**: SMS alerts via Twilio integration
- **Data Analysis**: Python backend for processing government data
- **Modern UI**: React/TypeScript frontend with responsive design
- **Cloud Deployment**: AWS infrastructure for scalability
- **Secure Authentication**: User account management and preferences

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- React Query for data fetching
- React Router for navigation

### Backend
- FastAPI (Python)
- PostgreSQL database
- OpenAI API for AI features
- Twilio for SMS notifications
- AWS services (Lambda, RDS, S3, etc.)

### Infrastructure
- AWS Lambda for serverless functions
- AWS RDS for database
- AWS S3 for static assets
- AWS SES for email notifications
- GitHub Actions for CI/CD

## Project Structure

```
CityCamp_AI/
├── frontend/           # React/TypeScript application
├── backend/            # Python FastAPI backend
├── infrastructure/     # AWS deployment configurations
├── docs/              # Project documentation
└── scripts/           # Build and deployment scripts
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL
- AWS CLI configured
- Twilio account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CityCamp_AI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Configure your environment variables
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Database Setup**
   ```bash
   # Run migrations
   cd backend
   alembic upgrade head
   ```

## Environment Variables

See `.env.example` files in both `frontend` and `backend` directories for required environment variables.

## Deployment

Deployment is automated through GitHub Actions and AWS infrastructure as code.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details 