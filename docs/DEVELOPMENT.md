# Development Guide

## Environment Setup

1. Copy `.env.example` to `.env`
2. Install dependencies: `make install`
3. Run migrations: `make migrate`
4. Start development: `make dev`

## Backend Development

### Settings Modules

| Module | Purpose |
|--------|---------|
| `config.settings.development` | Local development |
| `config.settings.production` | Production deployment |
| `config.settings.testing` | Test suite |

### Running Tests

```bash
cd backend
pytest ../backend/tests -v
pytest ../backend/tests --cov=. --cov-report=html
```

### Code Quality

```bash
make lint       # Check all linters
make format     # Auto-format code
make typecheck  # mypy + TypeScript
make security   # Bandit + Safety
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Frontend Development

```bash
cd frontend
npm run dev          # Dev server on :5173
npm run build        # Production build
npm run test         # Vitest
npm run lint         # ESLint
npm run typecheck    # TypeScript
```

## Docker Development

```bash
make docker-up       # Build and start all services
make logs            # Tail logs
make health          # Check health endpoints
make down            # Stop services
```

## Celery

```bash
# Worker
celery -A config worker --loglevel=info

# Beat scheduler
celery -A config beat --loglevel=info
```

## API Documentation

- Swagger UI: `/api/docs/swagger/`
- ReDoc: `/api/docs/redoc/`
- OpenAPI Schema: `/api/schema/`

## Branch Strategy

- `main` — production-ready code
- `develop` — integration branch
- `feature/*` — feature branches
- Conventional Commits required
