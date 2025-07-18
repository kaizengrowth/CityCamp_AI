# CityCamp AI - Tulsa Civic Engagement Platform

A modern CivicTech application that connects Tulsa residents with their city government through automated notifications, AI-powered assistance, and community organizing tools.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd CityCamp_AI

# Backend setup
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cp env.example .env

# Frontend setup  
cd ../frontend && npm install

# Start development servers
npm run dev  # Frontend (port 3002)
# In another terminal:
cd ../backend && uvicorn app.main:app --reload --port 8001  # Backend
```

## 🌟 Features

- **📅 Meeting Notifications** - Automated alerts for Tulsa City Council meetings
- **🤖 AI Assistant** - Interactive chatbot for city government questions  
- **📧 Email Generation** - AI-powered tool to contact representatives
- **🏛️ Meeting Minutes** - Real-time access to city council proceedings
- **👥 Community Platform** - Connect with other residents and organize

## 🏗️ Architecture

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + PostgreSQL + Redis
- **Infrastructure**: AWS (ECS, S3, CloudFront, RDS)
- **CI/CD**: GitHub Actions with automated testing and deployment

## 📁 Project Structure

```
CityCamp_AI/
├── 📚 docs/                  # All documentation
├── 🧪 tests/                 # Centralized test files
│   ├── backend/              # Python/FastAPI tests  
│   └── frontend/             # React/TypeScript tests
├── 🎨 frontend/              # React application
├── ⚙️ backend/               # FastAPI backend
├── ☁️ aws/                   # Infrastructure as code
└── 🔧 scripts/               # Build and deployment scripts
```

## 📖 Documentation

**All documentation is organized in the [`docs/`](docs/) directory:**

- **🚀 [Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **🔧 [CI/CD Setup](docs/GITHUB_ACTIONS_SETUP.md)** - GitHub Actions deployment
- **☁️ [AWS Deployment](docs/aws-deployment-guide.md)** - Production deployment guide
- **🐛 [Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **🧪 [Testing Guide](tests/README.md)** - How to run and write tests

## 🧪 Testing

**All tests are centralized in the [`tests/`](tests/) directory:**

```bash
# Backend tests
cd backend && python -m pytest ../tests/backend/ -v

# Frontend tests  
cd frontend && npm test

# All tests (CI)
# Automatically run via GitHub Actions on PRs and main branch
```

## 🌐 Live Application

**Production**: https://d1s9nkkr0t3pmn.cloudfront.net

## 🤝 Contributing

1. **Read the docs**: Start with [`docs/QUICKSTART.md`](docs/QUICKSTART.md)
2. **Run tests**: Follow [`tests/README.md`](tests/README.md)
3. **Create PR**: Tests run automatically via GitHub Actions
4. **Deploy**: Merging to `main` triggers automated deployment

## 📊 Project Status

- ✅ **Backend API** - FastAPI with PostgreSQL
- ✅ **Frontend** - React with TypeScript  
- ✅ **Database** - Meeting data and user management
- ✅ **Authentication** - User accounts and preferences
- ✅ **AWS Infrastructure** - Production-ready deployment
- ✅ **CI/CD Pipeline** - Automated testing and deployment
- 🔄 **Meeting Scraper** - Tulsa City Council data integration

## 🛡️ Security

- 🔐 **Environment variables** for secrets
- 🔑 **IAM roles** with minimal permissions  
- 🛡️ **Security scanning** in CI/CD pipeline
- 📊 **Monitoring** with AWS CloudWatch

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Check the [documentation](docs/) or [troubleshooting guide](docs/TROUBLESHOOTING.md)!
# Test CI/CD
