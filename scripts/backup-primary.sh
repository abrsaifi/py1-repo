#!/bin/bash
# Database backup script for primary PostgreSQL instance
# Part of Phase 3 Task 9: Disaster Recovery
# Usage: ./backup-primary.sh [backup_dir] [retention_days]

set -e

# Configuration
BACKUP_DIR="${1:-.backup}"
RETENTION_DAYS="${2:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"
LOG_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.log"

# Database configuration (from environment or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-docpro}"
DB_USER="${DB_USER:-postgres}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

log "========== Database Backup Started =========="
log "Timestamp: ${TIMESTAMP}"
log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
log "User: ${DB_USER}"
log "Backup location: ${BACKUP_FILE}"

# Pre-backup checks
log "Running pre-backup checks..."

# Check if psql is available
if ! command -v pg_dump &> /dev/null; then
    log "${RED}ERROR: pg_dump not found. Install PostgreSQL client tools.${NC}"
    exit 1
fi

# Test database connection
if ! PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1;" &>/dev/null; then
    log "${RED}ERROR: Cannot connect to database ${DB_NAME}@${DB_HOST}${NC}"
    exit 1
fi

log "${GREEN}✓ Database connection successful${NC}"

# Get database size before backup
DB_SIZE=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));" 2>/dev/null || echo "unknown")
log "Database size: ${DB_SIZE}"

# Perform backup
log "Starting full database dump..."
START_TIME=$(date +%s)

if PGPASSWORD="${DB_PASSWORD}" pg_dump \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --format=plain \
    --compress=9 \
    --verbose \
    --no-password \
    "${DB_NAME}" 2>>"${LOG_FILE}" | gzip -9 > "${BACKUP_FILE}"; then
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Get backup file size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    
    log "${GREEN}✓ Backup completed successfully${NC}"
    log "Backup size: ${BACKUP_SIZE}"
    log "Duration: ${DURATION} seconds"
    
    # Calculate compression ratio
    ORIGINAL_SIZE=$(PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT pg_database_size('${DB_NAME}');" 2>/dev/null || echo "0")
    if [ "${ORIGINAL_SIZE}" -gt 0 ]; then
        BACKUP_SIZE_BYTES=$(stat -f%z "${BACKUP_FILE}" 2>/dev/null || stat -c%s "${BACKUP_FILE}")
        COMPRESSION_RATIO=$(echo "scale=2; (100 * ${BACKUP_SIZE_BYTES}) / ${ORIGINAL_SIZE}" | bc)
        log "Compression ratio: ${COMPRESSION_RATIO}%"
    fi
else
    log "${RED}ERROR: Backup failed${NC}"
    exit 1
fi

# Verify backup integrity
log "Verifying backup integrity..."
if gzip -t "${BACKUP_FILE}" 2>/dev/null; then
    log "${GREEN}✓ Backup integrity verified${NC}"
else
    log "${RED}ERROR: Backup file is corrupted${NC}"
    rm -f "${BACKUP_FILE}"
    exit 1
fi

# Calculate checksum
log "Calculating SHA256 checksum..."
CHECKSUM=$(sha256sum "${BACKUP_FILE}" | cut -d' ' -f1)
echo "${CHECKSUM}  ${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"
log "Checksum: ${CHECKSUM}"

# Cleanup old backups
log "Cleaning up backups older than ${RETENTION_DAYS} days..."
DELETED_COUNT=0
while IFS= read -r old_backup; do
    if [ -f "${old_backup}" ]; then
        log "Deleting old backup: ${old_backup}"
        rm -f "${old_backup}"
        rm -f "${old_backup}.sha256"
        rm -f "${old_backup%.sql.gz}.log"
        ((DELETED_COUNT++))
    fi
done < <(find "${BACKUP_DIR}" -maxdepth 1 -name "backup_*.sql.gz" -mtime "+${RETENTION_DAYS}")

log "${GREEN}✓ Deleted ${DELETED_COUNT} old backup(s)${NC}"

# Final summary
log ""
log "========== Backup Summary =========="
log "Status: SUCCESS"
log "Backup file: ${BACKUP_FILE}"
log "File size: ${BACKUP_SIZE}"
log "Checksum: ${CHECKSUM}"
log "Timestamp: ${TIMESTAMP}"
log "Duration: ${DURATION} seconds"
log "========================================="

exit 0
