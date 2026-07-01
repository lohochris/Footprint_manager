# Folder Structure Guide

## Root

```text
Footprint_manager/
|-- .devcontainer/          # VS Code dev container config
|-- .github/workflows/      # CI/CD pipelines
|-- architecture/           # Architecture documents and reviews
|-- backend/                # Django backend
|-- docker/                 # Docker and Nginx configs
|-- docs/                   # Project documentation
|-- frontend/               # React frontend
|-- requirements/           # Python dependency files
|-- docker-compose.yml      # Docker Compose stack
|-- Makefile                # Development commands
|-- pyproject.toml          # Python tool configuration
`-- .env.example            # Environment template
```

## Backend

```text
backend/
|-- config/
|   |-- settings/
|   |   |-- base.py
|   |   |-- development.py
|   |   |-- production.py
|   |   `-- testing.py
|   |-- urls.py
|   |-- wsgi.py
|   |-- asgi.py
|   `-- celery.py
|-- apps/
|   |-- accounts/
|   |-- ai/
|   |-- audit/
|   |-- dashboard/
|   |-- integrations/
|   |-- notifications/
|   |-- organizations/
|   `-- rbac/
|-- core/
|   |-- health/
|   |-- logging/
|   |-- middleware/
|   `-- models/
|-- common/                 # Compatibility re-exports for core
|-- shared/
|   |-- cache/
|   |-- constants/
|   |-- enums/
|   |-- events/
|   |-- event_bus/
|   |-- exceptions/
|   |-- pagination/
|   |-- permissions/
|   |-- search/
|   |-- security/
|   |-- storage/
|   |-- types/
|   |-- utils/
|   `-- validators/
|-- scripts/
|-- tests/
`-- manage.py
```

## App Module Structure

```text
apps/<app_name>/
|-- admin/
|-- api/
|-- models/
|-- selectors/
|-- services/
|-- permissions/
|-- tasks/
|-- tests/
|-- migrations/
`-- apps.py
```

## Frontend

```text
frontend/src/
|-- assets/
|-- components/
|-- hooks/
|-- layouts/
|-- modules/
|-- pages/
|-- router/
|-- services/
|-- store/
|-- theme/
|-- types/
`-- utils/
```

