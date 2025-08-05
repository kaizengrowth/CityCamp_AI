# CityCamp AI Documentation

Welcome to the CityCamp AI documentation! This directory contains all project documentation organized by topic.

**🆕 New**: The **Tulsa Archive Scraper** system can now scrape **ALL historical documents** (2020-2025) from the official City of Tulsa Council Archive, supporting **16 different meeting types** including Regular Council, committees, and task forces. See [TULSA_ARCHIVE_SCRAPER_README.md](TULSA_ARCHIVE_SCRAPER_README.md) for complete details.

## 📚 Documentation Index

### 🚀 Getting Started
- **[README.md](README.md)** - Main project overview and quick start guide
- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup for local development

### 🔧 Setup & Configuration
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Environment variables and .env files guide
- **[AWS_CLI_SETUP.md](AWS_CLI_SETUP.md)** - AWS CLI installation guide (avoid committing installers!)
- **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** - Complete CI/CD setup guide
- **[aws-deployment-guide.md](aws-deployment-guide.md)** - AWS deployment options and guide

### 🐛 Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

### 🧪 Testing & Development
- **[SCRAPER_TEST_README.md](SCRAPER_TEST_README.md)** - Scraper testing documentation
- **[../tests/README.md](../tests/README.md)** - Test organization and running guide

### 🕸️ Data Collection & Scraping
- **[TULSA_ARCHIVE_SCRAPER_README.md](TULSA_ARCHIVE_SCRAPER_README.md)** - Comprehensive historical document scraping system

## 📁 Project Structure

```
CityCamp_AI/
├── docs/                  # 📚 All documentation (you are here!)
├── tests/                 # 🧪 All test files
│   ├── backend/          # Python/FastAPI tests
│   └── frontend/         # React/TypeScript tests
├── frontend/             # 🎨 React frontend application
├── backend/              # ⚙️ Python FastAPI backend
├── aws/                  # ☁️ AWS infrastructure code
└── scripts/              # 🔧 Build and deployment scripts
```

## 🎯 Quick Navigation

### For Developers
1. **First time setup**: [QUICKSTART.md](QUICKSTART.md)
2. **Running tests**: [../tests/README.md](../tests/README.md)
3. **Having issues?**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### For DevOps
1. **AWS deployment**: [aws-deployment-guide.md](aws-deployment-guide.md)
2. **CI/CD setup**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

### For Testing
1. **Test organization**: [../tests/README.md](../tests/README.md)
2. **Scraper testing**: [SCRAPER_TEST_README.md](SCRAPER_TEST_README.md)

### For Data Collection
1. **Historical scraping**: [TULSA_ARCHIVE_SCRAPER_README.md](TULSA_ARCHIVE_SCRAPER_README.md)
2. **Meeting discovery**: [SCRAPER_TEST_README.md](SCRAPER_TEST_README.md)

## 🔗 External Links

- **Live Application**: https://d1s9nkkr0t3pmn.cloudfront.net
- **GitHub Repository**: [Your GitHub URL]
- **AWS Console**: [Your AWS Console]

## 📝 Contributing to Documentation

When adding new documentation:

1. **Place files in the `docs/` directory**
2. **Use descriptive filenames** (e.g., `feature-name-guide.md`)
3. **Update this index** to include your new documentation
4. **Follow the existing markdown style**

### Documentation Standards

- Use clear, descriptive headings
- Include code examples where helpful
- Add troubleshooting sections for complex topics
- Keep documentation up-to-date with code changes

## 🏷️ Documentation Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **Setup Guides** | Initial configuration | QUICKSTART.md, GITHUB_ACTIONS_SETUP.md |
| **Deployment** | Production deployment | aws-deployment-guide.md |
| **Troubleshooting** | Problem solving | TROUBLESHOOTING.md |
| **Testing** | Test documentation | SCRAPER_TEST_README.md |
| **Architecture** | System design docs | (Add as needed) |

---

**Need help?** Check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide or create an issue in the GitHub repository.
