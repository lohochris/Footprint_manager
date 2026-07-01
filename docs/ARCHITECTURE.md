# Architecture Overview

Footprint Manager follows a modular monolith architecture for Phase 1. The repository is structured so shared contracts, domain apps, and infrastructure can be separated cleanly without introducing microservice complexity during Sprint 0.

## Backend Layers

| Layer | Responsibility |
| --- | --- |
| API | Request and response handling, serialization, OpenAPI schema generation |
| Services | Business logic orchestration in future sprints |
| Selectors | Read-optimized data queries in future sprints |
| Models | Abstract model foundations only in Sprint 0.1 |
| Shared | Cross-cutting contracts, primitives, events, cache, search, storage, validators |
| Core | Health, logging, tracing middleware, base model mixins |
| Common | Compatibility facade that re-exports core infrastructure |

## Domain Applications

| App | Current Scope |
| --- | --- |
| `accounts` | Sprint 0 bootstrap package only |
| `organizations` | Sprint 0 bootstrap package only |
| `rbac` | Sprint 0 bootstrap package only |
| `audit` | Sprint 0 bootstrap package only |
| `notifications` | Sprint 0 bootstrap package only |
| `dashboard` | Sprint 0 bootstrap package only |
| `apps.integrations` | Interface contracts for external providers |
| `apps.ai` | Interface contracts for AI gateway, providers, prompts, embeddings, memory, and RAG |

## Cross-Cutting Concerns

- Structured logging with `structlog`.
- Request and correlation IDs through core middleware.
- Health endpoints at `/health/`, `/health/live/`, and `/health/ready/`.
- OpenAPI through drf-spectacular.
- Feature flags configured through `FEATURE_FLAGS` and shared constants.
- Event contracts through `BaseDomainEvent`, `EventDispatcher`, and `EventHandler`.

## Frontend Architecture

- React 18 with TypeScript.
- Material UI theme foundations.
- Redux Toolkit and RTK Query bootstrap.
- Light and dark theme preparation.
- Responsive breakpoint and design-token structure.

## Infrastructure

- Docker Compose for local development.
- PostgreSQL as primary datastore.
- Redis for cache and Celery broker.
- Celery and django-celery-beat configured.
- GitHub Actions, pre-commit, ruff, pytest, and Vitest for quality gates.

## Sprint 0.1 Boundary

Sprint 0.1 does not implement authentication endpoints, RBAC rules, organizations, provider clients, business logic, application APIs, or concrete database entities beyond approved abstract mixins.

