#!/usr/bin/env bash
# =============================================================================
# seed.sh - Footprint Manager database seeding
# =============================================================================
# Runs database preparation steps that are safe for Sprint 0.1.
#
# Usage:
#   bash backend/scripts/seed.sh [--reset]
#
# Arguments:
#   --reset  Drop existing data before running migrations in development.
#
# Environment:
#   DJANGO_SETTINGS_MODULE defaults to config.settings.development.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${PROJECT_ROOT}/.venv"

RESET_MODE=false
if [[ "${1:-}" == "--reset" ]]; then
    RESET_MODE=true
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.development}"
export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH:-}"

log() { echo "[seed] $*"; }

if [[ "${DJANGO_SETTINGS_MODULE}" == *"production"* ]]; then
    echo "[seed] ERROR: Refusing to seed production database." >&2
    exit 1
fi

if [ -z "${VIRTUAL_ENV:-}" ] && [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
fi

cd "${BACKEND_DIR}"

if [ "${RESET_MODE}" = true ]; then
    log "Flushing existing data."
    python manage.py flush --no-input
fi

log "Running migrations."
python manage.py migrate --no-input

log "No seed datasets are defined for Sprint 0.1."
log "Database seeding complete."
