# 00_MASTER_ARCHITECTURE_GUIDE.md

# Footprint Manager — Master Architecture Guide
**Version:** 1.0  
**Status:** Authoritative Engineering Constitution  
**Audience:** Architects, Developers, AI Coding Assistants, DevOps, QA

---

# 1. Purpose

This document is the primary architectural constitution for the Footprint Manager platform.

Every engineer and every AI coding assistant (Cursor, Claude, ChatGPT, Gemini, Codex, etc.) **must read this document before implementing or modifying any part of the system**.

If any conflict exists between generated code and this guide, **this guide takes precedence**.

---

# 2. Vision

Footprint Manager is an enterprise-grade platform for:

- Digital Footprint Intelligence
- OSINT Investigation
- Identity Resolution
- Knowledge Graph Analysis
- Investigation Management
- Compliance Monitoring
- AI-Assisted Risk Intelligence

The platform is designed to be secure, scalable, modular, cloud-native, AI-ready, and suitable for enterprise and government deployment.

---

# 3. Authoritative Documents

Implementation must align with:

1. PRD
2. BTDS
3. SAD
4. ADR
5. DDS
6. ACS
7. ESG

No implementation may contradict these documents.

---

# 4. Core Architectural Principles

- Enterprise First
- Security by Design
- API First
- Domain-Driven Design (DDD)
- Modular Monolith (Phase 1)
- Event-Driven Ready
- Multi-Tenant First
- Cloud Native
- AI Ready
- Testability First
- Observability First
- Backward Compatibility

---

# 5. Technology Stack

## Backend
- Python 3.12+
- Django 5+
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- SimpleJWT

## Frontend
- React 18
- TypeScript
- Material UI
- Redux Toolkit
- RTK Query

## Infrastructure
- Docker
- Docker Compose
- Nginx
- GitHub Actions

## Future
- Neo4j
- Elasticsearch/OpenSearch
- Kafka
- OpenAI
- Claude
- Local LLM

---

# 6. Project Structure

```
architecture/
backend/
frontend/
docs/
```

Backend apps:

```
accounts/
organizations/
rbac/
audit/
notifications/
dashboard/
common/
shared/
```

Every app must contain:

```
admin/
api/
models/
selectors/
services/
permissions/
tasks/
tests/
migrations/
```

---

# 7. Engineering Rules

- Never hardcode configuration.
- Never bypass RBAC.
- Never violate tenant isolation.
- Never duplicate business logic.
- No business logic inside views or serializers.
- Reads belong in Selectors.
- Business logic belongs in Services.
- Use UUIDs for primary keys.
- Use structured logging.
- Every feature must include tests.
- Every API must be documented.
- Every migration must be reversible.
- Prefer composition over inheritance.

---

# 8. Security Rules

- JWT authentication
- Argon2 password hashing
- HTTPS everywhere
- OWASP ASVS compliance
- Immutable audit logs
- Principle of least privilege
- Secrets via environment variables
- No sensitive information in logs

---

# 9. Development Workflow

```
Architecture
    ↓
Sprint Planning
    ↓
Implementation
    ↓
Testing
    ↓
Architecture Review
    ↓
Merge
```

Never skip the architecture review.

---

# 10. Sprint Process

Each sprint must include:

- Scope
- Implementation
- Tests
- Documentation
- Review
- Approval

No sprint advances until approved.

---

# 11. Definition of Ready

A task is ready when:

- Requirements are approved
- Architecture is defined
- APIs are specified
- Database impacts are understood
- Acceptance criteria exist

---

# 12. Definition of Done

A feature is complete only if:

- Code compiles
- Tests pass
- Documentation updated
- OpenAPI updated
- Logging implemented
- Permissions enforced
- Architecture preserved
- Code reviewed

---

# 13. AI Coding Assistant Instructions

Before writing code:

1. Read this guide.
2. Read the architecture documents.
3. Implement only the current sprint.
4. Do not implement future sprints.
5. Do not invent architecture.
6. Ask for clarification when requirements conflict.
7. Preserve modularity.

---

# 14. Coding Philosophy

- Readability over cleverness
- Explicit over implicit
- Maintainability over speed
- Security over convenience
- Quality over quantity

---

# 15. Version Control

- Conventional Commits
- Git Flow
- Pull Requests required
- CI must pass before merge
- Main branch always deployable

---

# 16. Architecture Review Report (ARR)

Every sprint ends with an ARR containing:

- Architecture Score
- Security Score
- Code Quality Score
- Test Coverage
- Performance Notes
- Risks
- Technical Debt
- Approval (YES/NO)

---

# Final Statement

Footprint Manager is to be engineered as a long-term enterprise platform.
Every architectural decision should improve maintainability, scalability, security, and developer experience.
Shortcuts that compromise these principles are not permitted.
