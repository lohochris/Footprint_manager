#!/usr/bin/env bash
# =============================================================================
# lint.sh — Footprint Manager linting runner
# =============================================================================
# Runs all configured linters against the backend Python source.
#
# Usage:
#   bash backend/scripts/lint.sh [--fix]
#
# Arguments:
#   --fix  Pass to ruff to auto-fix lint violations where possible.
#
# Linters:
#   ruff   — fast Python linter (replaces flake8, isort, pyupgrade)
#   mypy   — static type checker (optional, only runs if mypy is installed)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${PROJECT_ROOT}/.venv"

FIX_MODE=false
if [[ "${1:-}" == "--fix" ]]; then
    FIX_MODE=true
fi

log()    { echo "[lint] $*"; }
success(){ echo "[lint] ✓ $*"; }
warn()   { echo "[lint] ⚠ $*"; }

# Activate virtual environment if needed
if [ -z "${VIRTUAL_ENV:-}" ] && [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
fi

cd "${PROJECT_ROOT}"

# ---------------------------------------------------------------------------
# ruff — linting
# ---------------------------------------------------------------------------
log "Running ruff linter..."
if [ "${FIX_MODE}" = true ]; then
    ruff check backend/ --fix
else
    ruff check backend/
fi
success "ruff lint passed."

# ---------------------------------------------------------------------------
# mypy — type checking (optional)
# ---------------------------------------------------------------------------
if command -v mypy &>/dev/null; then
    log "Running mypy type checker..."
    mypy backend/ --ignore-missing-imports || warn "mypy reported issues (non-blocking)."
    success "mypy completed."
else
    warn "mypy not installed — skipping type check."
fi

log "All lint checks completed."
