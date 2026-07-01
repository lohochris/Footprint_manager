# Footprint Manager

Enterprise Digital Footprint Intelligence Platform — Sprint 0 Infrastructure Bootstrap.

## Overview

Footprint Manager is an enterprise-grade platform for digital footprint intelligence, OSINT investigation, identity resolution, and compliance monitoring. This repository contains the Sprint 0 infrastructure foundation.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python 3.12, Django 5, DRF, PostgreSQL, Redis, Celery |
| Frontend | React 18, TypeScript, Material UI, Redux Toolkit, RTK Query |
| DevOps | Docker, Docker Compose, Nginx, GitHub Actions |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (local development)
- Node.js 20+ (local development)
- Make (optional)

### Docker (Recommended)

```bash
cp .env.example .env
docker compose up -d --build
```

Services:

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/swagger/ |
| ReDoc | http://localhost:8000/api/docs/redoc/ |
| Frontend | http://localhost:3000 |
| Nginx Proxy | http://localhost:8080 |
| Health Check | http://localhost:8000/health/ |

### Local Development

```bash
# Backend
cp .env.example .env
pip install -r requirements/development.txt -r requirements/testing.txt
cd backend && python manage.py migrate
cd backend && python manage.py runserver

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Project Structure

```
Footprint_manager/
├── backend/           # Django backend
│   ├── config/        # Settings, URLs, Celery, WSGI
│   ├── apps/          # Domain applications
│   ├── common/        # Shared infrastructure
│   ├── shared/        # Cross-cutting utilities
│   ├── scripts/       # Utility scripts
│   └── tests/         # Integration tests
├── frontend/          # React frontend
│   └── src/           # Source code
├── docker/            # Dockerfiles & Nginx configs
├── docs/              # Documentation
├── requirements/      # Python dependencies
└── .github/           # CI/CD workflows
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Folder Structure](docs/FOLDER_STRUCTURE.md)
- [Coding Standards](docs/CODING_STANDARDS.md)

## Testing

```bash
make test              # Run all tests
make test-backend      # Backend with coverage
make test-frontend     # Frontend Vitest
make lint              # All linters
make security          # Bandit + Safety
```

## Health Checks

```bash
curl http://localhost:8000/health/
curl http://localhost:8000/health/ready/
curl http://localhost:8000/health/live/
```

## License

Proprietary — All rights reserved.
