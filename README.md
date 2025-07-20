# 🏛️ CityCamp AI - Tulsa Civic Engagement Platform

A comprehensive CivicTech platform connecting Tulsa residents with city government through AI-powered tools, automated notifications, and intelligent meeting analytics.

## 📊 Project Status & Info

[![Build Status](https://github.com/kaizengrowth/CityCamp_AI/actions/workflows/ci.yml/badge.svg)](https://github.com/kaizengrowth/CityCamp_AI/actions)
[![Deployment Status](https://img.shields.io/badge/deployment-live-brightgreen)](https://d1s9nkkr0t3pmn.cloudfront.net)
[![Security](https://img.shields.io/badge/security-0_vulnerabilities-green)](https://github.com/kaizengrowth/CityCamp_AI)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[![GitHub release](https://img.shields.io/github/v/release/kaizengrowth/CityCamp_AI?include_prereleases)](https://github.com/kaizengrowth/CityCamp_AI/releases)
[![GitHub last commit](https://img.shields.io/github/last-commit/kaizengrowth/CityCamp_AI)](https://github.com/kaizengrowth/CityCamp_AI/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/kaizengrowth/CityCamp_AI)](https://github.com/kaizengrowth/CityCamp_AI/issues)
[![GitHub stars](https://img.shields.io/github/stars/kaizengrowth/CityCamp_AI)](https://github.com/kaizengrowth/CityCamp_AI/stargazers)

[![Tech Stack](https://img.shields.io/badge/stack-React%2BFastAPI%2BPostgreSQL-blue)](#-architecture)
[![Code Size](https://img.shields.io/github/languages/code-size/kaizengrowth/CityCamp_AI)](https://github.com/kaizengrowth/CityCamp_AI)
[![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)](#-system-status--health)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 📱 Application Screenshots

> **🌐 Live Demo**: [https://d1s9nkkr0t3pmn.cloudfront.net](https://d1s9nkkr0t3pmn.cloudfront.net)

### **🏠 Homepage & Dashboard**
*Coming Soon: Screenshots showcasing the main landing page, user dashboard, and navigation interface*

<!--
![Homepage](docs/screenshots/homepage/landing-page-desktop.png)
*Modern landing page with civic engagement call-to-action*

![Dashboard](docs/screenshots/homepage/dashboard-overview-desktop.png)
*Personalized user dashboard with meeting notifications*
-->

### **📅 Meeting Analytics & Search**
*Coming Soon: Screenshots demonstrating AI-powered meeting organization and search*

<!--
![Meeting List](docs/screenshots/meetings/meeting-list-desktop.png)
*AI-categorized meeting list with 42+ topic filters*

![Meeting Details](docs/screenshots/meetings/meeting-details-desktop.png)
*Detailed meeting view with agenda extraction and impact analysis*
-->

### **🤖 AI-Powered Civic Assistant**
*Coming Soon: Screenshots showcasing the interactive chatbot and AI responses*

<!--
![Chatbot Interface](docs/screenshots/chatbot/chatbot-interface-desktop.png)
*AI assistant responding to civic questions*

![Query Examples](docs/screenshots/chatbot/query-examples-desktop.png)
*Natural language queries about city government*
-->

### **📧 Smart Notifications & Email Generation**
*Coming Soon: Screenshots featuring notification preferences and AI-generated communications*

<!--
![Notification Signup](docs/screenshots/notifications/signup-form-desktop.png)
*Topic-based notification preferences interface*

![Email Generation](docs/screenshots/notifications/email-generation-desktop.png)
*AI-powered email composer for contacting representatives*
-->

### **📊 Admin Dashboard & Analytics**
*Coming Soon: Screenshots highlighting data management and analytics features*

<!--
![Data Import](docs/screenshots/admin/data-import-desktop.png)
*Meeting data import and AI processing interface*

![Analytics Dashboard](docs/screenshots/admin/analytics-dashboard-desktop.png)
*Usage analytics and user engagement metrics*
-->

### **📸 How to Add Screenshots**

**Automated Capture** (Recommended):
```bash
# Install Playwright
npm install playwright

# Capture all screenshots automatically
node scripts/capture-screenshots.js

# Capture from local development
SCREENSHOT_URL=http://localhost:3007 node scripts/capture-screenshots.js
```

**Manual Process**:
1. Visit the [live application](https://d1s9nkkr0t3pmn.cloudfront.net)
2. Take high-quality screenshots (1920x1080 recommended)
3. Save to `docs/screenshots/` following the [naming conventions](docs/screenshots/README.md)
4. Uncomment the relevant image sections above
5. Update this README with the new screenshots

> 📸 **Note**: Screenshots will be added progressively. The automated script captures desktop, tablet, and mobile views. See [`docs/screenshots/README.md`](docs/screenshots/README.md) for detailed guidelines.

## 🌟 Features

### 🤖 **AI-Powered Civic Assistant**
- Interactive chatbot with real-time city council knowledge
- Natural language queries about Tulsa government
- Meeting summary generation and analysis

### 📅 **Smart Meeting Notifications**
- Automated alerts for city council meetings
- Topic-based subscriptions (housing, transportation, etc.)
- SMS and email delivery with AI-categorized content

### 📊 **Intelligent Meeting Analytics**
- AI categorization of 42+ civic topics
- Automated agenda extraction and impact assessment
- Searchable meeting minutes with keyword analysis

### 💬 **Representative Communication**
- AI-powered email generation to contact officials
- District-based representative lookup
- Pre-built templates for common civic issues

### 🗳️ **Community Engagement**
- Campaign tracking and petition management
- Neighborhood-based organizing tools
- User preference and notification management

## 🚀 Quick Start

### **Local Development**
```bash
# Clone repository
git clone https://github.com/kaizengrowth/CityCamp_AI.git
cd CityCamp_AI

# Option 1: Automated setup (recommended)
./scripts/start-dev.sh

# Option 2: Manual setup
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python -m app.main

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**Access Points:**
- 🎨 **Frontend**: http://localhost:3007
- ⚙️ **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

### **Production Access**
- 🌐 **Live Application**: https://d1s9nkkr0t3pmn.cloudfront.net
- 📊 **AWS Console**: [ECS Services](https://console.aws.amazon.com/ecs/)

## 🏗️ Architecture

### **Technology Stack**
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11 + PostgreSQL + Redis
- **AI/ML**: OpenAI GPT-4 + Custom categorization models
- **Infrastructure**: AWS (ECS Fargate, RDS, ElastiCache, S3, CloudFront)
- **CI/CD**: GitHub Actions with automated testing and deployment

### **System Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │────│  React Frontend │    │   FastAPI API   │
│  (CDN/Routing)  │    │   (Static SPA)  │    │   (Backend)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                └────────┬───────────────┘
                                         │
                       ┌─────────────────┼─────────────────┐
                       │                 │                 │
                ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
                │ PostgreSQL  │   │    Redis    │   │   OpenAI    │
                │   (RDS)     │   │  (Cache)    │   │    API      │
                └─────────────┘   └─────────────┘   └─────────────┘
```

## 📁 Project Structure

```
CityCamp_AI/
├── 🎨 frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Route components
│   │   ├── contexts/        # React contexts
│   │   └── config/          # API configuration
│   ├── package.json         # Dependencies
│   └── vite.config.ts       # Vite configuration
│
├── ⚙️ backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── scrapers/        # Data collection
│   ├── requirements.txt     # Python dependencies
│   └── main.py             # Application entry point
│
├── ☁️ aws/                   # Infrastructure as Code
│   ├── terraform/           # Terraform configurations
│   ├── scripts/             # Deployment scripts
│   └── README.md           # AWS deployment guide
│
├── 📚 docs/                  # Comprehensive documentation
│   ├── QUICKSTART.md        # 5-minute setup guide
│   ├── aws-deployment-guide.md
│   ├── TROUBLESHOOTING.md   # Issue resolution
│   └── API_DOCUMENTATION.md # API reference
│
├── 🧪 tests/                 # Centralized testing
│   ├── backend/             # Python API tests
│   ├── frontend/            # React component tests
│   └── README.md           # Testing instructions
│
└── 🔧 scripts/               # Development & deployment
    ├── start-dev.sh         # Local development setup
    ├── test_production_api.sh # Production diagnostics
    └── fix_production_api.sh  # Production issue fixes
```

## 🔧 Development

### **Environment Setup**
```bash
# Check requirements
node --version  # >= 18.0.0
python --version # >= 3.11.0
docker --version # Latest

# Setup with automation
./scripts/start-dev.sh

# Manual database setup (if needed)
./scripts/setup_database.py
```

### **Key Development Commands**
```bash
# Frontend
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run test         # Run component tests
npm run lint         # Code linting

# Backend
cd backend
source venv/bin/activate
python -m app.main   # Start development server
python -m pytest ../tests/backend/ -v  # Run API tests
python -m app.services.meeting_scraper  # Data collection

# Full system
./scripts/start-dev.sh     # Start all services
./scripts/test-all.sh      # Run all tests
```

## 🚀 Production Deployment

### **Automated Deployment**
```bash
# Deploy to AWS (requires AWS CLI configured)
./aws/scripts/deploy.sh

# Check production health
./scripts/test_production_api.sh

# Fix production issues
./scripts/fix_production_api.sh
```

### **Manual Deployment Steps**
1. **Infrastructure**: Deploy with Terraform (`aws/terraform/`)
2. **Backend**: ECS Fargate service with auto-scaling
3. **Frontend**: S3 + CloudFront distribution
4. **Database**: RDS PostgreSQL with automated backups
5. **Monitoring**: CloudWatch logs and alerts

## 📊 System Status & Health

### **✅ Current Status (January 2025)**
- 🟢 **Frontend**: React app with Vite 6.3.5, 0 vulnerabilities
- 🟢 **Backend**: FastAPI with 42+ meeting records imported
- 🟢 **Database**: PostgreSQL with 11 tables, full schema
- 🟢 **AI Services**: OpenAI integration for categorization
- 🟢 **Notifications**: SMS/Email with Twilio integration
- 🟢 **Production**: AWS deployment with CloudFront CDN
- 🟢 **CI/CD**: GitHub Actions with automated testing

### **Recent Fixes (December 2024 - January 2025)**
- ✅ **Security**: Fixed esbuild vulnerability (0.25.0+)
- ✅ **Dependencies**: Resolved npm lock conflicts
- ✅ **API**: Fixed production meeting details loading
- ✅ **Build**: Node.js 18+ compatibility restored
- ✅ **Frontend**: @heroicons/react dependency issues resolved

### **Performance Metrics**
- 📈 **API Response Time**: < 500ms average
- 📊 **Database**: 40+ meetings with full AI categorization
- 🔄 **Uptime**: 99%+ availability
- 💾 **Data**: AI-processed meeting minutes and agenda items

## 🧪 Testing

### **Run All Tests**
```bash
# Automated testing
npm run test           # Frontend unit tests
python -m pytest tests/backend/ -v  # Backend API tests

# Manual testing
./scripts/test_production_api.sh  # Production diagnostics
curl http://localhost:8000/health # Health checks
```

### **Test Coverage**
- ✅ **API Endpoints**: All CRUD operations
- ✅ **Database Models**: Meeting, User, Notification schemas
- ✅ **AI Services**: Text extraction and categorization
- ✅ **Frontend Components**: Key UI components
- ✅ **Production Health**: End-to-end API testing

## 🛠️ Troubleshooting

### **Common Issues & Quick Fixes**

**Meeting Details Not Loading:**
```bash
./scripts/fix_production_api.sh  # Automated fix
```

**Backend Won't Start:**
```bash
lsof -ti:8000 | xargs kill -9  # Kill conflicting processes
cd backend && source venv/bin/activate && python -m app.main
```

**Frontend Dependencies Issues:**
```bash
cd frontend && rm -rf node_modules package-lock.json && npm install
```

**Production API Issues:**
```bash
./scripts/test_production_api.sh  # Diagnose issues
./scripts/fix_production_api.sh   # Apply fixes
```

**More solutions**: See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

## 📚 Documentation

### **Getting Started**
- 🚀 **[Quick Start Guide](docs/QUICKSTART.md)** - 5-minute setup
- 🔧 **[Environment Setup](docs/ENVIRONMENT_SETUP.md)** - Detailed configuration
- 🧪 **[Testing Guide](tests/README.md)** - Testing procedures

### **Deployment & Operations**
- ☁️ **[AWS Deployment](docs/aws-deployment-guide.md)** - Production setup
- 🔄 **[CI/CD Setup](docs/GITHUB_ACTIONS_SETUP.md)** - Automated workflows
- 🛡️ **[Security Guide](docs/TROUBLESHOOTING.md#security)** - Security best practices

### **API & Development**
- 📖 **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- 🤖 **[Chatbot Guide](docs/ENHANCED_CHATBOT_GUIDE.md)** - AI assistant setup
- 🔧 **[Scraper Documentation](docs/SCRAPER_TEST_README.md)** - Data collection

## 🤝 Contributing

### **Development Workflow**
1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/CityCamp_AI.git`
3. **Setup**: Run `./scripts/start-dev.sh`
4. **Develop**: Make changes and test locally
5. **Test**: Run `npm test` and `python -m pytest tests/backend/ -v`
6. **Submit**: Create pull request

### **Code Standards**
- ✅ **TypeScript**: Strict mode enabled
- ✅ **Python**: Type hints and docstrings
- ✅ **Testing**: Unit tests for new features
- ✅ **Linting**: Pre-commit hooks configured
- ✅ **Documentation**: Update README for new features

## 📊 Monitoring & Analytics

### **Production Monitoring**
- 📈 **CloudWatch**: Application and infrastructure metrics
- 🔍 **Logs**: Centralized logging with search capabilities
- 🚨 **Alerts**: Automated notifications for issues
- 📊 **Dashboard**: Real-time system health metrics

### **Key Metrics**
- 🌐 **Web Traffic**: CloudFront analytics
- 📱 **API Usage**: Request volume and response times
- 💾 **Database**: Query performance and connection health
- 🤖 **AI Services**: API usage and categorization accuracy

## 🔐 Security

### **Security Features**
- 🛡️ **HTTPS**: All communication encrypted
- 🔐 **Environment Variables**: Secrets management
- 🏗️ **VPC**: Network isolation in AWS
- 👤 **IAM**: Minimal permission roles
- 🔍 **Security Scanning**: Automated vulnerability checks

### **Data Protection**
- 📊 **Database Encryption**: At rest and in transit
- 🔒 **API Authentication**: JWT tokens
- 🛡️ **Input Validation**: XSS and injection prevention
- 📋 **Audit Logs**: Comprehensive activity tracking

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Get Help**
- 📚 **Documentation**: Check [`docs/`](docs/) directory
- 🐛 **Issues**: Create GitHub issue with details
- 💬 **Discussions**: Use GitHub Discussions for questions
- 🛠️ **Emergency**: Run `./scripts/fix_production_api.sh` for production issues

### **Contact**
- 📧 **Email**: [Contact information if available]
- 🐙 **GitHub**: [@kaizengrowth](https://github.com/kaizengrowth)

---

## 📈 Recent Updates

**Latest Changes** (January 2025):
- ✅ Fixed production meeting details loading issues
- ✅ Added comprehensive production troubleshooting scripts
- ✅ Resolved security vulnerabilities (esbuild, dependencies)
- ✅ Enhanced CI/CD pipeline with automated testing
- ✅ Updated documentation and README files

**Next Planned Features**:
- 🔄 Enhanced meeting data scraping automation
- 📱 Mobile app development
- 🤖 Advanced AI categorization improvements
- 📊 User analytics dashboard

---

**Ready to get started?** Follow the [Quick Start Guide](docs/QUICKSTART.md) or run `./scripts/start-dev.sh`! 🚀
