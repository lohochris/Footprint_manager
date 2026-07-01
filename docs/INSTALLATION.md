# Installation Guide

## System Requirements

- **OS**: Linux, macOS, or Windows with WSL2
- **Docker**: 24.0+ with Compose V2
- **Python**: 3.12+ (local dev)
- **Node.js**: 20 LTS (local dev)
- **PostgreSQL**: 16 (via Docker or local)
- **Redis**: 7 (via Docker or local)

## Docker Installation (Recommended)

1. Clone the repository:

```bash
git clone <repository-url>
cd Footprint_manager
```

2. Create environment file:

```bash
cp .env.example .env
```

3. Edit `.env` and set a secure `SECRET_KEY` and `JWT_SIGNING_KEY`.

4. Start the stack:

```bash
docker compose up -d --build
```

5. Verify services:

```bash
curl http://localhost:8000/health/
curl http://localhost:8000/api/docs/swagger/
```

## Local Installation

### Backend

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements/development.txt -r requirements/testing.txt -r requirements/linting.txt
cp .env.example .env
cd backend
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Supporting Services

Start PostgreSQL and Redis locally, or use Docker for services only:

```bash
docker compose up -d db redis
```

## Dev Container

Open the project in VS Code/Cursor and select **Reopen in Container** when prompted. The dev container includes all tools pre-configured.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection refused | Ensure PostgreSQL is running and `DATABASE_URL` is correct |
| Redis connection failed | Ensure Redis is running on port 6379 |
| Port already in use | Change ports in `docker-compose.yml` or stop conflicting services |
| Static files missing | Run `python manage.py collectstatic` |
