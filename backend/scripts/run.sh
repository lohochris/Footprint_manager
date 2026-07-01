#!/usr/bin/env bash
# =============================================================================
# run.sh — Footprint Manager development server launcher
# =============================================================================
# Starts the Django development server with the correct settings and PYTHONPATH.
#
# Usage:
#   bash backend/scripts/run.sh [port]
#
# Arguments:
#   port  — TCP port to bind (default: 8000)
#
# Environment:
#   DJANGO_SETTINGS_MODULE  — override settings module (default: development)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${PROJECT_ROOT}/.venv"

PORT="${1:-8000}"
SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.development}"

log() { echo "[run] $*"; }

# Activate virtual environment if not already active
if [ -z "${VIRTUAL_ENV:-}" ] && [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
fi

export DJANGO_SETTINGS_MODULE="${SETTINGS_MODULE}"
export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH:-}"

log "Starting Footprint Manager on http://0.0.0.0:${PORT}"
log "Settings: ${SETTINGS_MODULE}"

cd "${BACKEND_DIR}"
exec python manage.py runserver "0.0.0.0:${PORT}"
