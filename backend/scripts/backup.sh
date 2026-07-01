#!/usr/bin/env bash
# =============================================================================
# backup.sh — Footprint Manager PostgreSQL database backup
# =============================================================================
# Creates a timestamped compressed dump of the PostgreSQL database.
# Suitable for manual backups and scheduled cron jobs.
#
# Usage:
#   bash backend/scripts/backup.sh [output_dir]
#
# Arguments:
#   output_dir  — Directory to write the backup file (default: ./backups)
#
# Environment variables read from .env:
#   DATABASE_URL  — PostgreSQL connection URL
#
# Output file format:
#   footprint_manager_YYYY-MM-DD_HHMMSS.dump
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

OUTPUT_DIR="${1:-${PROJECT_ROOT}/backups}"
TIMESTAMP="$(date '+%Y-%m-%d_%H%M%S')"
BACKUP_FILE="${OUTPUT_DIR}/footprint_manager_${TIMESTAMP}.dump"

log()  { echo "[backup] $*"; }
fail() { echo "[backup] ERROR: $*" >&2; exit 1; }

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

command -v pg_dump &>/dev/null || fail "pg_dump not found. Install PostgreSQL client tools."

mkdir -p "${OUTPUT_DIR}"

log "Creating backup: ${BACKUP_FILE}"
pg_dump \
    --format=custom \
    --compress=9 \
    --no-acl \
    --no-owner \
    "${DATABASE_URL}" \
    --file="${BACKUP_FILE}"

BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
log "Backup complete: ${BACKUP_FILE} (${BACKUP_SIZE})"
log "To restore: bash backend/scripts/restore.sh ${BACKUP_FILE}"
