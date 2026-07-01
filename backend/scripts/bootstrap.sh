#!/usr/bin/env bash
# =============================================================================
# bootstrap.sh — Footprint Manager development environment setup
# =============================================================================
# Sets up the complete local development environment from a clean checkout.
# Run this once after cloning the repository.
#
# Usage:
#   bash backend/scripts/bootstrap.sh
#
# Prerequisites:
#   - Python 3.12+
#   - pip / venv
#   - Docker Desktop (for PostgreSQL + Redis)
#   - Node.js 20+ (for frontend)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${PROJECT_ROOT}/.venv"

log()  { echo "[bootstrap] $*"; }
fail() { echo "[bootstrap] ERROR: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# 1. Python version check
# ---------------------------------------------------------------------------
log "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_MAJOR=3
REQUIRED_MINOR=12
MAJOR=$(echo "${PYTHON_VERSION}" | cut -d. -f1)
MINOR=$(echo "${PYTHON_VERSION}" | cut -d. -f2)

if [ "${MAJOR}" -lt "${REQUIRED_MAJOR}" ] || { [ "${MAJOR}" -eq "${REQUIRED_MAJOR}" ] && [ "${MINOR}" -lt "${REQUIRED_MINOR}" ]; }; then
    fail "Python ${REQUIRED_MAJOR}.${REQUIRED_MINOR}+ required, found ${PYTHON_VERSION}."
fi
log "Python ${PYTHON_VERSION} — OK"

# ---------------------------------------------------------------------------
# 2. Virtual environment
# ---------------------------------------------------------------------------
if [ ! -d "${VENV_DIR}" ]; then
    log "Creating virtual environment at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
log "Virtual environment activated."

# ---------------------------------------------------------------------------
# 3. Install Python dependencies
# ---------------------------------------------------------------------------
log "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r "${PROJECT_ROOT}/requirements/development.txt" --quiet
log "Python dependencies installed."

# ---------------------------------------------------------------------------
# 4. Copy environment file
# ---------------------------------------------------------------------------
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    log "Copying .env.example → .env"
    cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
    log "Edit ${PROJECT_ROOT}/.env before running services."
else
    log ".env already exists — skipping."
fi

# ---------------------------------------------------------------------------
# 5. Install pre-commit hooks
# ---------------------------------------------------------------------------
if command -v pre-commit &>/dev/null; then
    log "Installing pre-commit hooks..."
    cd "${PROJECT_ROOT}" && pre-commit install
    log "Pre-commit hooks installed."
else
    log "pre-commit not found — skipping hook installation."
fi

# ---------------------------------------------------------------------------
# 6. Install frontend dependencies
# ---------------------------------------------------------------------------
if command -v npm &>/dev/null; then
    log "Installing frontend dependencies..."
    cd "${PROJECT_ROOT}/frontend" && npm install --silent
    log "Frontend dependencies installed."
else
    log "npm not found — skipping frontend setup."
fi

log "Bootstrap complete. Run 'bash backend/scripts/run.sh' to start the development server."
