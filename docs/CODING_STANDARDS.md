# Coding Standards Summary

Based on the Engineering Standards Guide (ESG) and Master Architecture Guide.

## General Principles

- Readability over cleverness
- Explicit over implicit
- Security over convenience
- Testability first

## Backend (Python/Django)

### Architecture Rules

- No business logic in views or serializers
- Reads belong in **Selectors**
- Business logic belongs in **Services**
- Use UUIDs for primary keys
- Use structured logging (structlog)
- Environment variables for all configuration

### Code Style

| Tool | Purpose |
|------|---------|
| Ruff | Linting |
| Black | Formatting (100 char line length) |
| isort | Import sorting |
| mypy | Type checking |
| Bandit | Security linting |

### Naming Conventions

- Models: `PascalCase` singular (`Organization`)
- Services: verb phrases (`create_organization`)
- Selectors: noun phrases (`get_active_users`)
- API URLs: kebab-case (`/api/v1/organizations/`)

## Frontend (TypeScript/React)

### Architecture Rules

- Feature modules for domain separation
- RTK Query for API calls
- React Hook Form + Zod for forms
- No business logic in components

### Code Style

| Tool | Purpose |
|------|---------|
| ESLint | Linting |
| Prettier | Formatting |
| TypeScript strict mode | Type safety |

### Naming Conventions

- Components: `PascalCase` (`AppHeader.tsx`)
- Hooks: `camelCase` with `use` prefix (`useAppDispatch`)
- Types/Interfaces: `PascalCase` (`HealthResponse`)
- Constants: `UPPER_SNAKE_CASE`

## Git Conventions

- **Conventional Commits**: `feat:`, `fix:`, `chore:`, `docs:`, `test:`
- Pull requests required for all changes
- CI must pass before merge

## Testing

- Every feature must include tests
- Backend: pytest + factory_boy
- Frontend: Vitest + Testing Library
- Minimum coverage tracked via CI

## Security

- Never hardcode secrets
- Never log sensitive data
- Argon2 for password hashing
- JWT for authentication (Sprint 1+)
- OWASP ASVS compliance target
