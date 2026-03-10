#!/bin/bash
# Setup PostgreSQL standby server with continuous streaming replication
# Part of Phase 3 Task 9: Disaster Recovery
# Usage: ./setup-standby.sh [primary_host] [standby_data_dir] [replication_slot_name]

set -e

# Configuration
PRIMARY_HOST="${1:-localhost}"
PRIMARY_PORT="${2:-5432}"
STANDBY_DATA_DIR="${3:-/var/lib/postgresql/standby-data}"
REPLICATION_SLOT_NAME="${4:-standby_slot_1}"
REPLICATION_USER="${5:-replication}"

# Database configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-docpro}"
DB_SUPERUSER="${DB_SUPERUSER:-postgres}"
STANDBY_PORT="${STANDBY_PORT:-5433}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

success() {
    echo -e "${GREEN}✓ $*${NC}"
}

error() {
    echo -e "${RED}✗ ERROR: $*${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root (needed for postgresql data directory operations)"
    exit 1
fi

log "========== PostgreSQL Standby Setup Started =========="
log "Primary server: ${PRIMARY_HOST}:${PRIMARY_PORT}"
log "Standby data directory: ${STANDBY_DATA_DIR}"
log "Replication slot: ${REPLICATION_SLOT_NAME}"
log "Replication user: ${REPLICATION_USER}"

# Pre-checks
log ""
log "Running pre-setup checks..."

# Check PostgreSQL client tools
if ! command -v pg_basebackup &> /dev/null; then
    error "pg_basebackup not found. Install PostgreSQL client tools."
    exit 1
fi
success "PostgreSQL client tools found"

# Check if primary is reachable
if ! timeout 5 bash -c "echo > /dev/tcp/${PRIMARY_HOST}/${PRIMARY_PORT}" 2>/dev/null; then
    error "Cannot reach primary server ${PRIMARY_HOST}:${PRIMARY_PORT}"
    exit 1
fi
success "Primary server is reachable"

# Check if standby data directory exists
if [ -d "${STANDBY_DATA_DIR}" ]; then
    log "Standby data directory exists. Checking if empty..."
    if [ "$(ls -A ${STANDBY_DATA_DIR})" ]; then
        error "Standby data directory is not empty: ${STANDBY_DATA_DIR}"
        error "Please remove existing data or specify a different directory"
        exit 1
    fi
    success "Standby data directory is empty"
else
    log "Creating standby data directory: ${STANDBY_DATA_DIR}"
    mkdir -p "${STANDBY_DATA_DIR}"
    chmod 700 "${STANDBY_DATA_DIR}"
    chown postgres:postgres "${STANDBY_DATA_DIR}"
    success "Standby data directory created"
fi

# Check if standby can connect to primary (with replication user)
log "Testing replication user connection to primary..."
if PGPASSWORD="${REPLICATION_PASSWORD}" psql \
    -h "${PRIMARY_HOST}" \
    -U "${REPLICATION_USER}" \
    -d "${DB_NAME}" \
    -c "SELECT version();" &>/dev/null; then
    success "Replication user connection successful"
else
    error "Cannot connect with replication user"
    error "Ensure replication user '${REPLICATION_USER}' exists on primary"
    exit 1
fi

# Check replication permissions on primary
log "Verifying replication permissions..."
REPLICATION_CHECK=$(PGPASSWORD="${REPLICATION_PASSWORD}" psql \
    -h "${PRIMARY_HOST}" \
    -U "${REPLICATION_USER}" \
    -t -c "SELECT usereplication FROM pg_user WHERE usename='${REPLICATION_USER}';" 2>/dev/null || echo "f")

if [ "${REPLICATION_CHECK}" != "t" ]; then
    error "Replication user does not have REPLICATION privilege on primary"
    exit 1
fi
success "Replication permissions verified"

# Perform base backup
log ""
log "Starting base backup from primary..."
log "This may take a few minutes depending on database size..."

START_TIME=$(date +%s)

if pg_basebackup \
    --host="${PRIMARY_HOST}" \
    --port="${PRIMARY_PORT}" \
    --username="${REPLICATION_USER}" \
    --dbname="postgresql://replication@${PRIMARY_HOST}:${PRIMARY_PORT}/${DB_NAME}" \
    --pgdata="${STANDBY_DATA_DIR}" \
    --progress \
    --write-recovery-conf \
    --wal-method=stream \
    --format=plain; then
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    success "Base backup completed in ${DURATION} seconds"
else
    error "Base backup failed"
    exit 1
fi

# Update standby recovery configuration
log ""
log "Configuring standby recovery settings..."

# Create recovery configuration in postgresql.conf
cat >> "${STANDBY_DATA_DIR}/postgresql.conf" <<EOF

# === Standby Recovery Configuration ===
primary_conninfo = 'host=${PRIMARY_HOST} port=${PRIMARY_PORT} user=${REPLICATION_USER} password=${REPLICATION_PASSWORD} dbname=${DB_NAME}'
primary_slot_name = '${REPLICATION_SLOT_NAME}'

# Hot standby settings
hot_standby = on
hot_standby_feedback = on

# Recovery settings
recovery_timeout = 30s
wal_retrieve_retry_interval = 5s

EOF

success "Recovery configuration added to postgresql.conf"

# Create standby signal file (PostgreSQL 12+)
touch "${STANDBY_DATA_DIR}/standby.signal"
chmod 600 "${STANDBY_DATA_DIR}/standby.signal"
chown postgres:postgres "${STANDBY_DATA_DIR}/standby.signal"

success "Standby signal file created"

# Fix permissions
chown -R postgres:postgres "${STANDBY_DATA_DIR}"
chmod 700 "${STANDBY_DATA_DIR}"

success "Permissions configured"

# Create recovery.conf alternative (for compatibility)
cat > "${STANDBY_DATA_DIR}/recovery.conf.standby" <<EOF
# PostgreSQL Standby Recovery Configuration
# This file documents the standby recovery setup

# Connection to primary
standby_mode = 'on'
primary_conninfo = 'host=${PRIMARY_HOST} port=${PRIMARY_PORT} user=${REPLICATION_USER} password=${REPLICATION_PASSWORD} dbname=${DB_NAME}'
primary_slot_name = '${REPLICATION_SLOT_NAME}'

# Hot standby settings  
hot_standby = on
hot_standby_feedback = on

# Recovery settings
recovery_target_timeline = 'latest'
recovery_timeout = 30s
wal_retrieve_retry_interval = 5s

# Archive recovery settings (if WAL archiving is enabled)
restore_command = 'cp /var/lib/postgresql/wal_archive/%f "%p"'
archive_cleanup_command = 'pg_archivecleanup /var/lib/postgresql/wal_archive "%%" %r'

# Logging
log_connections = on
log_disconnections = on
log_replication_commands = on

# Performance tuning
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 32MB

EOF

success "Recovery configuration file created: recovery.conf.standby"

log ""
log "========== Standby Setup Summary =========="
log "Status: SUCCESS"
log "Primary server: ${PRIMARY_HOST}:${PRIMARY_PORT}"
log "Standby data directory: ${STANDBY_DATA_DIR}"
log "Replication slot: ${REPLICATION_SLOT_NAME}"
log "Standby port: ${STANDBY_PORT}"
log "Duration: ${DURATION} seconds"
log ""
log "Next steps:"
log "1. Start the standby PostgreSQL service:"
log "   sudo systemctl start postgresql (if using systemd)"
log "   or"
log "   sudo -u postgres /usr/lib/postgresql/XX/bin/postgres -D ${STANDBY_DATA_DIR}"
log ""
log "2. Verify replication is working:"
log "   psql -h ${PRIMARY_HOST} -U postgres -c 'SELECT * FROM pg_stat_replication;'"
log "   or (on standby):"
log "   psql -h localhost -p ${STANDBY_PORT} -U postgres -c 'SELECT pg_is_in_recovery();'"
log ""
log "3. Check standby lag:"
log "   psql -h ${PRIMARY_HOST} -U postgres -c 'SELECT now() - pg_last_wal_receive_lsn() as replication_lag;'"
log ""
log "========== Setup Complete =========="

exit 0
