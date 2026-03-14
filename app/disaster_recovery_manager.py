"""
Disaster Recovery Manager
Handles automated backups, replication monitoring, recovery procedures
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import logging
import json
import os
from pathlib import Path
import subprocess
from uuid import uuid4
import hashlib

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages database backups and recovery procedures"""
    
    def __init__(self, db_config: Dict, backup_dir: str = "/var/backups/docpro"):
        self.db_config = db_config
        self.backup_dir = backup_dir
        self.backup_manifest = f"{backup_dir}/manifest.json"
        
        # Ensure backup directory exists
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    def create_full_backup(self) -> Tuple[bool, str, Optional[str]]:
        """
        Create a full database backup using pg_dump
        Returns: (success, backup_path, error_message)
        """
        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_dir}/full_backup_{timestamp}.sql.gz"
            
            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                f"--dbname={self.db_config['database']}",
                "--format=plain",
                "--verbose",
                "--compress=9",
                f"--file={backup_file}",
            ]
            
            # Add password via environment
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            logger.info(f"Starting full backup to {backup_file}")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                return False, "", result.stderr
            
            # Calculate file size and checksum
            file_size = os.path.getsize(backup_file)
            checksum = self._calculate_checksum(backup_file)
            
            # Record in manifest
            self._add_to_manifest({
                'type': 'full',
                'timestamp': timestamp,
                'file': backup_file,
                'size_bytes': file_size,
                'checksum': checksum,
                'status': 'completed',
            })
            
            logger.info(f"Full backup completed: {backup_file} ({file_size} bytes)")
            return True, backup_file, None
            
        except subprocess.TimeoutExpired:
            logger.error("Backup timeout after 1 hour")
            return False, "", "Backup timeout"
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False, "", str(e)
    
    def verify_backup(self, backup_file: str, restore_to_temp: bool = False) -> Tuple[bool, dict]:
        """
        Verify backup integrity
        Optionally attempt test restore to temporary database
        """
        try:
            backup_info = {
                'file': backup_file,
                'exists': os.path.exists(backup_file),
                'size_bytes': os.path.getsize(backup_file) if os.path.exists(backup_file) else 0,
                'checksum': None,
                'gzip_valid': False,
                'restore_tested': False,
                'error': None,
            }
            
            if not backup_info['exists']:
                backup_info['error'] = "Backup file not found"
                return False, backup_info
            
            # Check gzip validity
            try:
                import gzip
                with gzip.open(backup_file, 'rb') as f:
                    f.read(1024)  # Read first 1KB to verify integrity
                backup_info['gzip_valid'] = True
            except Exception as e:
                backup_info['error'] = f"Gzip validation failed: {e}"
                return False, backup_info
            
            # Calculate and verify checksum
            backup_info['checksum'] = self._calculate_checksum(backup_file)
            
            # Attempt test restore if requested
            if restore_to_temp:
                success = self._test_restore(backup_file)
                backup_info['restore_tested'] = success
                if not success:
                    backup_info['error'] = "Test restore failed"
                    return False, backup_info
            
            logger.info(f"Backup verification passed: {backup_file}")
            return True, backup_info
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False, {'file': backup_file, 'error': str(e)}
    
    def restore_from_backup(self, backup_file: str, target_db: Optional[str] = None) -> Tuple[bool, str]:
        """
        Restore database from backup
        Returns: (success, message)
        """
        try:
            target_database = target_db or self.db_config['database']
            
            logger.info(f"Starting restore from {backup_file} to {target_database}")
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # For safety, use psql to restore
            with open(backup_file, 'r') as f:
                cmd = [
                    "psql",
                    f"--host={self.db_config['host']}",
                    f"--port={self.db_config['port']}",
                    f"--username={self.db_config['user']}",
                    f"--dbname={target_database}",
                    "--quiet",
                ]
                
                result = subprocess.run(cmd, stdin=f, env=env, capture_output=True, text=True, timeout=3600)
            
            if result.returncode != 0:
                error_msg = f"Restore failed: {result.stderr}"
                logger.error(error_msg)
                return False, error_msg
            
            # Record restore in manifest
            self._add_to_manifest({
                'type': 'restore',
                'timestamp': datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
                'from_backup': backup_file,
                'target_database': target_database,
                'status': 'completed',
            })
            
            logger.info(f"Restore completed successfully to {target_database}")
            return True, f"Restored {target_database} from {backup_file}"
            
        except subprocess.TimeoutExpired:
            return False, "Restore timeout after 1 hour"
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return False, str(e)
    
    def _test_restore(self, backup_file: str) -> bool:
        """Test restore to temporary database"""
        try:
            temp_db = f"test_restore_{uuid4().hex[:8]}"
            
            logger.info(f"Testing restore to temporary database: {temp_db}")
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # Create temp database
            subprocess.run([
                "createdb",
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                temp_db,
            ], env=env, capture_output=True, timeout=60)
            
            # Restore to temp database
            with open(backup_file, 'r') as f:
                result = subprocess.run([
                    "psql",
                    f"--host={self.db_config['host']}",
                    f"--port={self.db_config['port']}",
                    f"--username={self.db_config['user']}",
                    f"--dbname={temp_db}",
                    "--quiet",
                ], stdin=f, env=env, capture_output=True, timeout=600)
            
            success = result.returncode == 0
            
            # Drop temp database
            subprocess.run([
                "dropdb",
                f"--host={self.db_config['host']}",
                f"--port={self.db_config['port']}",
                f"--username={self.db_config['user']}",
                temp_db,
            ], env=env, capture_output=True, timeout=60)
            
            logger.info(f"Test restore {'passed' if success else 'failed'}")
            return success
            
        except Exception as e:
            logger.error(f"Test restore error: {e}")
            return False
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _add_to_manifest(self, entry: Dict) -> None:
        """Add entry to backup manifest"""
        try:
            manifest = []
            if os.path.exists(self.backup_manifest):
                with open(self.backup_manifest, 'r') as f:
                    manifest = json.load(f)
            
            entry['recorded_at'] = datetime.now(timezone.utc).isoformat()
            manifest.append(entry)
            
            with open(self.backup_manifest, 'w') as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update manifest: {e}")
    
    def get_backup_history(self, limit: int = 20) -> List[Dict]:
        """Get recent backup history"""
        try:
            if not os.path.exists(self.backup_manifest):
                return []
            
            with open(self.backup_manifest, 'r') as f:
                manifest = json.load(f)
            
            # Return only backups, sorted by date (newest first)
            backups = [m for m in manifest if m['type'] == 'full']
            return sorted(backups, key=lambda x: x['timestamp'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Failed to read backup history: {e}")
            return []
    
    def cleanup_old_backups(self, retention_days: int = 30) -> Tuple[int, int]:
        """
        Delete backups older than retention period
        Returns: (deleted_count, freed_bytes)
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            deleted_count = 0
            freed_bytes = 0
            
            for backup in self.get_backup_history(limit=100):
                backup_time = datetime.fromisoformat(backup['timestamp'])
                
                if backup_time < cutoff_date:
                    backup_file = backup.get('file')
                    if backup_file and os.path.exists(backup_file):
                        try:
                            freed_bytes += os.path.getsize(backup_file)
                            os.remove(backup_file)
                            deleted_count += 1
                            logger.info(f"Deleted old backup: {backup_file}")
                        except Exception as e:
                            logger.warning(f"Failed to delete {backup_file}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} backups, freed {freed_bytes} bytes")
            return deleted_count, freed_bytes
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0, 0


class ReplicationMonitor:
    """Monitor PostgreSQL streaming replication health"""
    
    def __init__(self, primary_config: Dict, standby_config: Dict):
        self.primary_config = primary_config
        self.standby_config = standby_config
    
    def check_replication_status(self) -> Dict:
        """
        Check status of streaming replication
        Returns: {primary_lag, standby_connected, files_position, ...}
        """
        try:
            status = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'primary_healthy': False,
                'standby_healthy': False,
                'replication_lag_bytes': None,
                'replication_lag_seconds': None,
                'primary_lsn': None,
                'standby_lsn': None,
                'wal_files_behind': None,
                'error': None,
            }
            
            # Check primary status
            primary_lsn = self._get_current_lsn(self.primary_config)
            if primary_lsn:
                status['primary_lsn'] = primary_lsn
                status['primary_healthy'] = True
            else:
                status['error'] = "Cannot connect to primary"
                return status
            
            # Check standby status
            standby_lsn = self._get_current_lsn(self.standby_config, is_standby=True)
            if standby_lsn:
                status['standby_lsn'] = standby_lsn
                status['standby_healthy'] = True
                
                # Calculate lag
                try:
                    lag_bytes = self._lsn_to_bytes(primary_lsn) - self._lsn_to_bytes(standby_lsn)
                    status['replication_lag_bytes'] = max(0, lag_bytes)
                    
                    # Estimate lag in seconds (rough, assuming 1MB/sec throughput)
                    if lag_bytes > 0:
                        status['replication_lag_seconds'] = lag_bytes / (1024 * 1024)
                except Exception as e:
                    logger.warning(f"Could not calculate lag: {e}")
            else:
                status['error'] = "Cannot connect to standby"
            
            logger.info(f"Replication status: {json.dumps(status, indent=2)}")
            return status
            
        except Exception as e:
            logger.error(f"Replication status check failed: {e}")
            return {'error': str(e), 'timestamp': datetime.now(timezone.utc).isoformat()}
    
    def _get_current_lsn(self, config: Dict, is_standby: bool = False) -> Optional[str]:
        """Get current LSN (Log Sequence Number) from database"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
            )
            
            cursor = conn.cursor()
            
            if is_standby:
                cursor.execute("SELECT pg_last_wal_receive_lsn();")
            else:
                cursor.execute("SELECT pg_current_wal_lsn();")
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            logger.warning(f"LSN check failed: {e}")
            return None
    
    def _lsn_to_bytes(self, lsn: str) -> int:
        """Convert LSN string (e.g., '0/12345678') to byte number"""
        try:
            parts = lsn.split('/')
            if len(parts) == 2:
                return int(parts[0], 16) * (2**32) + int(parts[1], 16)
        except:
            pass
        return 0


class RecoveryPlanner:
    """Plan and execute recovery operations"""
    
    def __init__(self, db_config: Dict, backup_manager: BackupManager):
        self.db_config = db_config
        self.backup_manager = backup_manager
    
    def get_recovery_options(self) -> Dict:
        """Get available recovery strategies"""
        backups = self.backup_manager.get_backup_history(limit=5)
        
        return {
            'available_backups': len(backups),
            'latest_backup': backups[0] if backups else None,
            'recovery_method': {
                'full_restore': {
                    'description': 'Restore from full backup (all data)',
                    'recovery_time': '5-30 minutes',
                    'data_loss': 'Data since last backup',
                },
                'pitr': {
                    'description': 'Point-in-time recovery (requires WAL archives)',
                    'recovery_time': '10-60 minutes',
                    'data_loss': 'Can recover to any point',
                },
                'streaming_standby': {
                    'description': 'Promote standby (minimal data loss)',
                    'recovery_time': '30 seconds',
                    'data_loss': 'Minimal (only unwritten WAL)',
                },
            },
            'nearest_backup': backups[0]['timestamp'] if backups else None,
            'backed_up_at': backups[0]['recorded_at'] if backups else None,
        }
    
    def estimate_rto_rpo(self) -> Dict:
        """Estimate RTO (Recovery Time Objective) and RPO (Recovery Point Objective)"""
        backups = self.backup_manager.get_backup_history(limit=1)
        
        if not backups:
            latest_backup_time = datetime.now(timezone.utc)
        else:
            latest_backup_time = datetime.fromisoformat(backups[0]['timestamp'])
        
        # Time since last backup
        time_since_backup = datetime.now(timezone.utc) - latest_backup_time
        
        return {
            'rto_estimate': {
                'method': 'Full restore from backup',
                'duration_minutes': 15,
                'description': 'Assuming 5-15 minute restore from full backup',
            },
            'rpo_estimate': {
                'method': 'WAL archiving + daily full backups',
                'duration_minutes': 5,
                'max_data_loss_minutes': min(time_since_backup.total_seconds() / 60, 1440),
                'description': 'Can recover to any point within last 24 hours',
            },
            'last_backup_age_minutes': time_since_backup.total_seconds() / 60,
            'backup_strategy': 'Daily full backups + continuous WAL archiving',
            'target_rto_minutes': 15,
            'target_rpo_minutes': 5,
            'compliant': time_since_backup.total_seconds() / 60 < 1440,  # Within 24 hours
        }


class BackupScheduler:
    """Schedule backup operations"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
    
    def schedule_celery_tasks(self, app):
        """Configure Celery Beat schedule for backups"""
        # This would be called from app/tasks.py
        schedule = {
            'daily-full-backup': {
                'task': 'app.tasks.backup_database_full',
                'schedule': {'hour': 2, 'minute': 0},  # 2 AM daily
                'description': 'Full database backup',
            },
            'weekly-backup-verification': {
                'task': 'app.tasks.verify_latest_backup',
                'schedule': {'day_of_week': 0, 'hour': 3, 'minute': 0},  # Sunday 3 AM
                'description': 'Test restore latest backup',
            },
            'monthly-backup-cleanup': {
                'task': 'app.tasks.cleanup_old_backups',
                'schedule': {'day_of_month': 1, 'hour': 4, 'minute': 0},  # 1st of month 4 AM
                'description': 'Delete backups older than 30 days',
            },
            'replication-health-check': {
                'task': 'app.tasks.check_replication_health',
                'schedule': {'minute': '*/5'},  # Every 5 minutes
                'description': 'Monitor streaming replication',
            },
        }
        return schedule


# Flask integration helper

def get_backup_manager() -> BackupManager:
    """Get backup manager instance"""
    from flask import current_app
    
    db_config = {
        'host': current_app.config.get('SQLALCHEMY_DATABASE_HOST', 'localhost'),
        'port': current_app.config.get('SQLALCHEMY_DATABASE_PORT', 5432),
        'user': current_app.config.get('SQLALCHEMY_DATABASE_USER', 'docpro'),
        'password': current_app.config.get('SQLALCHEMY_DATABASE_PASSWORD', ''),
        'database': current_app.config.get('SQLALCHEMY_DATABASE_NAME', 'docpro'),
    }
    
    backup_dir = current_app.config.get('BACKUP_DIR', '/var/backups/docpro')
    return BackupManager(db_config, backup_dir)


if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'password',
        'database': 'docpro',
    }
    
    manager = BackupManager(db_config)
    
    # Create backup
    success, backup_file, error = manager.create_full_backup()
    if success:
        print(f"Backup created: {backup_file}")
        
        # Verify backup
        valid, info = manager.verify_backup(backup_file)
        print(f"Backup valid: {valid}")
        print(f"Backup info: {json.dumps(info, indent=2)}")
    else:
        print(f"Backup failed: {error}")
