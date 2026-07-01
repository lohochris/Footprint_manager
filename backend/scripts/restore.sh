#!/usr/bin/env bash
# =============================================================================
# restore.sh — Footprint Manager PostgreSQL database restore
# =============================================================================
# Restores a database from a pg_dump custom-format backup file.
#
# Usage:
#   bash backend/scripts/restore.sh <backup_file> [--yes]
#
# Arguments:
#   backup_file  — Path to the .dump file created by backup.sh
#   --yes        — Skip confirmation prompt (CI / automated mode)
#
# Environment variables read from .env:
#   DATABASE_URL  — PostgreSQL connection URL
#
# WARNING: This operation replaces all data in the target database.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

BACKUP_FILE="${1:-}"
AUTO_YES=false
if [[ "${2:-}" == "--yes" ]]; then
    AUTO_YES=true
fi

log()  { echo "[restore] $*"; }
fail() { echo "[restore] ERROR: $*" >&2; exit 1; }

# Validate arguments
if [ -z "${BACKUP_FILE}" ]; then
    fail "Usage: bash restore.sh <backup_file> [--yes]"
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    fail "Backup file not found: ${BACKUP_FILE}"
fi

# Load DATABASE_URL from .env
if [ -f "${PROJECT_ROOT}/.env" ]; then
    # shellcheck disable=SC1091
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

DATABASE_URL="${DATABASE_URL:-}"
if [ -z "${DATABASE_URL}" ]; then
    fail "DATABASE_URL is not set. Check your .env file."
fi

# Safety: refuse to restore to production without explicit override
if [[ "${DJANGO_SETTINGS_MODULE:-}" == *"production"* ]] && [ "${AUTO_YES}" != true ]; then
    fail "Refusing to restore to production without --yes flag."
fi

command -v pg_restore &>/dev/null || fail "pg_restore not found. Install PostgreSQL client tools."

# Confirmation prompt
if [ "${AUTO_YES}" != true ]; then
    log "WARNING: This will REPLACE all data in the target database."
    log "Backup file : ${BACKUP_FILE}"
    log "Database    : ${DATABASE_URL}"
    read -r -p "[restore] Type 'restore' to confirm: " CONFIRM
    if [ "${CONFIRM}" != "restore" ]; then
        log "Restore cancelled."
        exit 0
    fi
fi

BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
log "Restoring from: ${BACKUP_FILE} (${BACKUP_SIZE})"

pg_restore \
    --format=custom \
    --clean \
    --no-acl \
    --no-owner \
    --dbname="${DATABASE_URL}" \
    "${BACKUP_FILE}"

log "Restore complete."
