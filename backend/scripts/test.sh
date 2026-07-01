#!/usr/bin/env bash
# =============================================================================
# test.sh — Footprint Manager test runner
# =============================================================================
# Runs the full test suite with coverage reporting.
#
# Usage:
#   bash backend/scripts/test.sh [pytest-args...]
#
# Examples:
#   bash backend/scripts/test.sh
#   bash backend/scripts/test.sh -k test_health
#   bash backend/scripts/test.sh --no-cov
#
# Environment:
#   DJANGO_SETTINGS_MODULE  — defaults to config.settings.testing
#   COVERAGE_THRESHOLD      — minimum coverage % to pass (default: 0)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
VENV_DIR="${PROJECT_ROOT}/.venv"

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.testing}"
export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH:-}"

log() { echo "[test] $*"; }

# Activate virtual environment if needed
if [ -z "${VIRTUAL_ENV:-}" ] && [ -d "${VENV_DIR}" ]; then
    # shellcheck disable=SC1091
    source "${VENV_DIR}/bin/activate"
fi

log "Running tests with settings: ${DJANGO_SETTINGS_MODULE}"

cd "${PROJECT_ROOT}"
exec pytest "${@:-}"
