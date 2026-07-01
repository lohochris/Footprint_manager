# Architecture Index

This directory contains the architectural documentation for the Footprint Manager platform.

| Category | Document | Description |
| --- | --- | --- |
| Constitution | [Master Architecture Guide](../00_MASTER_ARCHITECTURE_GUIDE.md) | Primary architectural constitution |
| Product | [PRD](../Footprint%20Manager%20Phase1%20PRD.docx) | Phase 1 product requirements |
| Backend | [BTDS](../Footprint%20Manager%20BTDS.docx) | Backend technical design specification |
| System | [SAD](../Footprint%20Manager%20SAD.docx) | System architecture document |
| Decisions | [ADR](../Footprint%20Manager%20ADR.docx) | Architecture decision records |
| Database | [DDS](../Footprint%20Manager%20DDS.docx) | Database design specification |
| API | [ACS](../Footprint%20Manager%20ACS.docx) | API contract specification |
| Standards | [ESG](../Footprint%20Manager%20ESG.docx) | Engineering standards guide |
| Developer Docs | [docs/](../docs/) | Installation, development, architecture, and folder guides |
| Sprint Reviews | [reviews/](./reviews/) | Per-sprint architecture review reports |

## Sprint Review History

| Sprint | Review | Status |
| --- | --- | --- |
| Sprint 0 and 0.1 | [SPRINT-000-REVIEW.md](./reviews/SPRINT-000-REVIEW.md) | Approved |

## Architecture Layers

```text
Frontend
  React 18, TypeScript, Material UI, Redux Toolkit

API Layer
  Django REST Framework, drf-spectacular, health endpoints

Domain Apps
  accounts, organizations, rbac, audit, notifications, dashboard

AI and Integration Foundations
  apps.ai, apps.integrations

Shared Layer
  constants, enums, exceptions, events, event_bus, pagination,
  permissions, security, validators, cache, search, storage, types, utils

Core Infrastructure
  health, logging, middleware, base model mixins

Compatibility Layer
  common re-exports core infrastructure for Sprint 0 import stability

Data and Runtime
  PostgreSQL, Redis, Celery, Docker, CI/CD
```

## Engineering Rules

- Use environment configuration for deploy-time settings.
- Keep UUID primary keys on persistent entities.
- Keep business logic in services and read queries in selectors.
- Document APIs through OpenAPI.
- Keep migrations reversible.
- Use structured logging with request and correlation IDs.
- Do not advance sprint scope without architecture review approval.

