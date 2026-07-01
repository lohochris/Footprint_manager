.PHONY: help install install-backend install-frontend dev up down build migrate test lint format clean docker-build docker-up docker-down coverage security

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python dependencies
	pip install -r requirements/development.txt -r requirements/testing.txt -r requirements/linting.txt

install-frontend: ## Install Node.js dependencies
	cd frontend && npm install

dev: ## Start development servers locally
	docker compose up -d db redis
	cd backend && python manage.py migrate --noinput
	cd backend && python manage.py runserver 0.0.0.0:8000 &
	cd frontend && npm run dev

up: ## Start full Docker stack
	docker compose up -d

down: ## Stop Docker stack
	docker compose down

build: ## Build Docker images
	docker compose build

migrate: ## Run Django migrations
	cd backend && python manage.py migrate

test: ## Run all tests
	cd backend && pytest ../backend/tests -v

test-backend: ## Run backend tests with coverage
	cd backend && pytest ../backend/tests -v --cov=. --cov-report=term-missing

test-frontend: ## Run frontend tests
	cd frontend && npm run test

lint: ## Run all linters
	cd backend && ruff check .
	cd backend && black --check .
	cd backend && isort --check-only .
	cd frontend && npm run lint

format: ## Format all code
	cd backend && ruff check --fix .
	cd backend && black .
	cd backend && isort .
	cd frontend && npm run format

typecheck: ## Run type checking
	cd backend && mypy backend/
	cd frontend && npm run typecheck

security: ## Run security scans
	cd backend && bandit -r backend/ -c pyproject.toml
	cd backend && safety check -r requirements/base.txt

coverage: ## Generate coverage report
	cd backend && pytest ../backend/tests --cov=. --cov-report=html

docker-build: ## Build production Docker images
	docker build -f docker/Dockerfile -t footprint-manager-backend .
	docker build -f docker/Dockerfile.frontend -t footprint-manager-frontend .

docker-up: ## Start production-like Docker stack
	docker compose up -d --build

docker-down: ## Stop and remove Docker containers
	docker compose down -v

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist frontend/node_modules/.vite

pre-commit: ## Install and run pre-commit hooks
	pre-commit install
	pre-commit run --all-files

shell: ## Open Django shell
	cd backend && python manage.py shell

createsuperuser: ## Create Django superuser
	cd backend && python manage.py createsuperuser

logs: ## Tail Docker logs
	docker compose logs -f

health: ## Check service health
	curl -s http://localhost:8000/health/ | python -m json.tool
	curl -s http://localhost:8000/health/ready/ | python -m json.tool
