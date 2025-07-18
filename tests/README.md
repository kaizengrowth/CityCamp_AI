# Tests Directory

This directory contains all test files for the CityCamp AI project, organized by component.

## Structure

```
tests/
├── backend/           # Backend Python tests
│   ├── __init__.py
│   ├── test_main.py   # Main API tests
│   ├── test_scraper.py # Scraper functionality tests
│   ├── simple_test.py # Database integration tests
│   ├── *.db          # Test databases
└── frontend/          # Frontend React/TypeScript tests
    ├── jest.config.js # Jest configuration
    ├── setupTests.ts  # Test setup and mocks
    └── App.test.tsx   # Component tests
```

## Running Tests

### Backend Tests

From the project root:

```bash
# Run all backend tests
cd backend && python -m pytest ../tests/backend/ -v

# Run with coverage
cd backend && python -m pytest ../tests/backend/ -v --cov=app --cov-report=html

# Run specific test file
cd backend && python -m pytest ../tests/backend/test_main.py -v
```

### Frontend Tests

From the project root:

```bash
# Run all frontend tests
cd frontend && npm test

# Run tests in CI mode (no watch)
cd frontend && npm run test:ci

# Run tests with watch mode
cd frontend && npm run test:watch
```

### All Tests (CI/CD)

The GitHub Actions workflows automatically run all tests:

- **Pull Requests**: Runs all tests and quality checks
- **Main Branch**: Runs tests before deployment

## Test Configuration

### Backend (pytest)

- **Framework**: pytest
- **Coverage**: pytest-cov
- **Database**: PostgreSQL test database
- **Mocking**: pytest-mock, factory-boy

### Frontend (Jest)

- **Framework**: Jest + React Testing Library
- **Environment**: jsdom
- **Coverage**: Built-in Jest coverage
- **Mocking**: Jest mocks for API calls

## Adding New Tests

### Backend Tests

1. Create test files in `tests/backend/`
2. Follow naming convention: `test_*.py`
3. Use pytest fixtures for setup
4. Mock external dependencies

Example:
```python
# tests/backend/test_new_feature.py
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_new_feature():
    response = client.get("/api/v1/new-feature")
    assert response.status_code == 200
```

### Frontend Tests

1. Create test files in `tests/frontend/`
2. Follow naming convention: `*.test.tsx`
3. Use React Testing Library utilities
4. Mock API calls and external dependencies

Example:
```typescript
// tests/frontend/NewComponent.test.tsx
import { render, screen } from '@testing-library/react';
import NewComponent from '../../frontend/src/components/NewComponent';

test('renders new component', () => {
  render(<NewComponent />);
  expect(screen.getByText('Hello World')).toBeInTheDocument();
});
```

## Test Data

- **Backend**: Test databases (`*.db` files) contain sample data for integration tests
- **Frontend**: Mock data is defined in test files or `setupTests.ts`

## Coverage Reports

Coverage reports are generated in:
- **Backend**: `backend/htmlcov/` (HTML) and `backend/coverage.xml` (XML)
- **Frontend**: `frontend/coverage/` (HTML and LCOV)

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every push to main branch
- Coverage reports are uploaded to Codecov

## Troubleshooting

### Backend Test Issues

```bash
# Install test dependencies
cd backend && pip install -r requirements-dev.txt

# Check Python path
cd backend && python -c "import sys; print(sys.path)"

# Run with verbose output
cd backend && python -m pytest ../tests/backend/ -v -s
```

### Frontend Test Issues

```bash
# Install dependencies
cd frontend && npm install

# Clear Jest cache
cd frontend && npm test -- --clearCache

# Run with debug output
cd frontend && npm test -- --verbose
```
