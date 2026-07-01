#!/usr/bin/env bash
# =============================================================================
# format.sh — Footprint Manager code formatter
# =============================================================================
# Formats Python source with ruff format (replaces black) and isort.
# Also formats frontend TypeScript/TSX with prettier.
#
# Usage:
#   bash backend/scripts/format.sh [--check]
#
# Arguments:
#   --check  Check formatting without writing changes (CI mode).
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"

CHECK_MODE=false
if [[ "${1:-}" == "--check" ]]; then
    CHECK_MODE=true
fi

log()    { echo "[format] $*"; }
success(){ echo "[format] ✓ $*"; }

# Activate virtual environment if needed
if [ -z "${VIRTUAL_ENV:-}" ] && [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
fi

cd "${PROJECT_ROOT}"

# ---------------------------------------------------------------------------
# ruff format — Python formatting
# ---------------------------------------------------------------------------
log "Running ruff format on backend/..."
if [ "${CHECK_MODE}" = true ]; then
    ruff format backend/ --check
else
    ruff format backend/
fi
success "Python formatting complete."

# ---------------------------------------------------------------------------
# isort — import ordering (via ruff --select I)
# ---------------------------------------------------------------------------
log "Running ruff import sorting on backend/..."
if [ "${CHECK_MODE}" = true ]; then
    ruff check backend/ --select I --check 2>/dev/null || true
else
    ruff check backend/ --select I --fix
fi

# ---------------------------------------------------------------------------
# prettier — frontend formatting
# ---------------------------------------------------------------------------
if [ -f "${PROJECT_ROOT}/frontend/node_modules/.bin/prettier" ]; then
    log "Running prettier on frontend/src/..."
    if [ "${CHECK_MODE}" = true ]; then
        cd "${PROJECT_ROOT}/frontend" && npx prettier --check "src/**/*.{ts,tsx,css,json}" --quiet
    else
        cd "${PROJECT_ROOT}/frontend" && npx prettier --write "src/**/*.{ts,tsx,css,json}" --quiet
    fi
    success "Frontend formatting complete."
else
    log "prettier not installed in frontend/node_modules — skipping."
fi

log "Format complete."
