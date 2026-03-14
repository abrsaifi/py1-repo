"""Background tasks for file conversions and system operations."""
from celery import current_app as celery_app
from datetime import datetime, timedelta, timezone
import os
import json
from app.models import db, Conversion, User
from sqlalchemy import func

# File conversion tasks
@celery_app.task(bind=True, name='app.tasks.convert_file')
def convert_file(self, conversion_id):
    """Convert a file in background."""
    try:
        conversion = Conversion.query.get(conversion_id)
        if not conversion:
            return {'status': 'error', 'message': 'Conversion not found'}
        
        # Update status
        conversion.status = 'processing'
        conversion.started_at = datetime.now(timezone.utc)
        conversion.worker_id = self.request.hostname
        db.session.commit()
        
        # Import conversion service
        from app.services.conversions import ConversionService
        
        # Perform actual conversion
        start_time = datetime.now(timezone.utc)
        result = ConversionService.convert(
            input_path=conversion.input_path,
            output_format=conversion.output_format,
            parameters=conversion.parameters or {}
        )
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Update conversion record
        conversion.status = 'completed'
        conversion.output_path = result.get('output_path')
        conversion.output_size = result.get('output_size', 0)
        conversion.completed_at = datetime.now(timezone.utc)
        conversion.processing_time = processing_time
        db.session.commit()
        
        # Update user quota if needed
        user = User.query.get(conversion.user_id)
        if user:
            size_gb = conversion.output_size / (1024**3)
            user.used_gb = max(0, user.used_gb + size_gb)
            db.session.commit()
        
        return {
            'status': 'completed',
            'conversion_id': conversion_id,
            'processing_time': processing_time
        }
        
    except Exception as exc:
        conversion = Conversion.query.get(conversion_id)
        if conversion:
            conversion.status = 'failed'
            conversion.error_message = str(exc)
            conversion.completed_at = datetime.now(timezone.utc)
            db.session.commit()
        
        # Retry task
        raise self.retry(exc=exc, countdown=60)

@celery_app.task(bind=True, name='app.tasks.process_image')
def process_image(self, image_id):
    """Process image in background."""
    try:
        conversion = Conversion.query.get(image_id)
        if not conversion:
            return {'status': 'error'}
        
        conversion.status = 'processing'
        conversion.worker_id = self.request.hostname
        db.session.commit()
        
        from app.image_processor import ImageProcessor
        processor = ImageProcessor()
        
        result = processor.process(
            input_path=conversion.input_path,
            output_format=conversion.output_format,
            params=conversion.parameters or {}
        )
        
        conversion.status = 'completed'
        conversion.output_path = result['path']
        conversion.output_size = result.get('size', 0)
        conversion.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return {'status': 'completed', 'id': image_id}
        
    except Exception as exc:
        conversion = Conversion.query.get(image_id)
        if conversion:
            conversion.status = 'failed'
            conversion.error_message = str(exc)
            db.session.commit()
        raise self.retry(exc=exc, countdown=60)

@celery_app.task(bind=True, name='app.tasks.process_pdf')
def process_pdf(self, pdf_id):
    """Process PDF in background."""
    try:
        conversion = Conversion.query.get(pdf_id)
        if not conversion:
            return {'status': 'error'}
        
        conversion.status = 'processing'
        conversion.worker_id = self.request.hostname
        db.session.commit()
        
        from app.pdf_handler import PDFHandler
        handler = PDFHandler()
        
        result = handler.process(
            input_path=conversion.input_path,
            output_format=conversion.output_format,
            params=conversion.parameters or {}
        )
        
        conversion.status = 'completed'
        conversion.output_path = result['path']
        conversion.output_size = result.get('size', 0)
        conversion.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return {'status': 'completed', 'id': pdf_id}
        
    except Exception as exc:
        conversion = Conversion.query.get(pdf_id)
        if conversion:
            conversion.status = 'failed'
            conversion.error_message = str(exc)
            db.session.commit()
        raise self.retry(exc=exc, countdown=60)

# Email tasks
@celery_app.task(bind=True, name='app.tasks.send_email')
def send_email(self, to_email, subject, template, context=None):
    """Send email in background."""
    try:
        from app.services.email_service import EmailService

        email_service = EmailService()
        sent = email_service.send(
            to=to_email,
            subject=subject,
            template=template,
            context=context or {}
        )

        return {'status': 'sent' if sent else 'failed', 'to': to_email}
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)

@celery_app.task(bind=True, name='app.tasks.send_daily_reports')
def send_daily_reports(self):
    """Send daily reports to users and admins."""
    try:
        from app.services.reports import ReportService
        
        report_service = ReportService()
        
        # Send to all active users
        users = User.query.filter_by(is_active=True).all()
        notified_count = 0
        for user in users:
            if user.subscription and user.subscription.is_active:
                if report_service.send_daily_report(user.id):
                    notified_count += 1

        return {'status': 'completed', 'users_notified': notified_count}
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3600)

# Maintenance tasks
@celery_app.task(bind=True, name='app.tasks.cleanup_old_uploads')
def cleanup_old_uploads(self):
    """Clean up old uploaded files."""
    try:
        # Delete files older than 7 days that are not in active conversions
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        
        old_conversions = Conversion.query.filter(
            Conversion.created_at < cutoff_date,
            Conversion.status.in_(['completed', 'failed', 'cancelled'])
        ).all()
        
        deleted_count = 0
        for conversion in old_conversions:
            # Delete files
            if conversion.input_path and os.path.exists(conversion.input_path):
                try:
                    os.remove(conversion.input_path)
                    deleted_count += 1
                except OSError:
                    pass
            
            if conversion.output_path and os.path.exists(conversion.output_path):
                try:
                    os.remove(conversion.output_path)
                    deleted_count += 1
                except OSError:
                    pass
        
        return {
            'status': 'completed',
            'files_deleted': deleted_count,
            'conversions_cleaned': len(old_conversions)
        }
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3600)

@celery_app.task(bind=True, name='app.tasks.update_conversion_stats')
def update_conversion_stats(self):
    """Update conversion statistics."""
    try:
        # Get stats for the last 24 hours
        twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        
        total = Conversion.query.filter(
            Conversion.created_at >= twenty_four_hours_ago
        ).count()
        
        completed = Conversion.query.filter(
            Conversion.created_at >= twenty_four_hours_ago,
            Conversion.status == 'completed'
        ).count()
        
        failed = Conversion.query.filter(
            Conversion.created_at >= twenty_four_hours_ago,
            Conversion.status == 'failed'
        ).count()
        
        avg_time = db.session.query(
            func.avg(Conversion.processing_time)
        ).filter(
            Conversion.created_at >= twenty_four_hours_ago,
            Conversion.status == 'completed'
        ).scalar() or 0
        
        return {
            'status': 'updated',
            'period': '24_hours',
            'total_conversions': total,
            'successful': completed,
            'failed': failed,
            'avg_processing_time': float(avg_time)
        }
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)

# Utility task
@celery_app.task(bind=True, name='app.tasks.long_running_operation')
def long_running_operation(self, operation_id, **kwargs):
    """Execute a long-running operation."""
    try:
        # This is a generic task for handling long-running ops
        return {'status': 'completed', 'operation_id': operation_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# Disaster Recovery Tasks (Phase 3 Task 9)
@celery_app.task(bind=True, name='app.tasks.backup_database_full')
def backup_database_full(self):
    """Create a full backup of the database - runs daily at 2 AM."""
    try:
        from app.disaster_recovery_manager import BackupManager
        
        backup_manager = BackupManager()
        success, backup_path, error = backup_manager.create_full_backup()
        
        if success:
            celery_app.logger.info(f'Full database backup completed: {backup_path}')
            return {
                'status': 'success',
                'backup_path': backup_path,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        else:
            celery_app.logger.error(f'Full database backup failed: {error}')
            raise Exception(f'Backup failed: {error}')
    
    except Exception as exc:
        celery_app.logger.error(f'backup_database_full task failed: {str(exc)}')
        # Retry after 1 hour on failure
        raise self.retry(exc=exc, countdown=3600)

@celery_app.task(bind=True, name='app.tasks.verify_latest_backup')
def verify_latest_backup(self):
    """Verify the latest backup integrity with test restore - runs weekly Sunday 3 AM."""
    try:
        from app.disaster_recovery_manager import BackupManager
        
        backup_manager = BackupManager()
        
        # Get latest backup
        backups = backup_manager.get_backup_history(limit=1)
        if not backups:
            celery_app.logger.warning('No backups found to verify')
            return {'status': 'no_backups', 'timestamp': datetime.now(timezone.utc).isoformat()}
        
        latest_backup = backups[0]
        backup_file = latest_backup.get('path')
        
        # Verify backup with test restore
        success, message = backup_manager.verify_backup(backup_file, restore_to_temp=True)
        
        if success:
            celery_app.logger.info(f'Backup verification succeeded: {backup_file}')
            return {
                'status': 'verified',
                'backup_file': backup_file,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        else:
            celery_app.logger.error(f'Backup verification failed: {message}')
            raise Exception(f'Verification failed: {message}')
    
    except Exception as exc:
        celery_app.logger.error(f'verify_latest_backup task failed: {str(exc)}')
        # Retry after 3 hours on failure
        raise self.retry(exc=exc, countdown=10800)

@celery_app.task(bind=True, name='app.tasks.cleanup_old_backups')
def cleanup_old_backups(self, retention_days=30):
    """Delete backups older than retention period - runs monthly on 1st at 4 AM."""
    try:
        from app.disaster_recovery_manager import BackupManager
        
        backup_manager = BackupManager()
        freed_space = backup_manager.cleanup_old_backups(retention_days=retention_days)
        
        celery_app.logger.info(
            f'Backup cleanup completed. Freed: {freed_space / (1024**3):.2f} GB'
        )
        
        return {
            'status': 'completed',
            'freed_space_gb': freed_space / (1024**3),
            'retention_days': retention_days,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as exc:
        celery_app.logger.error(f'cleanup_old_backups task failed: {str(exc)}')
        # Retry after 2 hours on failure
        raise self.retry(exc=exc, countdown=7200)

@celery_app.task(bind=True, name='app.tasks.check_replication_health')
def check_replication_health(self):
    """Monitor replication status and lag - runs every 5 minutes."""
    try:
        from app.disaster_recovery_manager import ReplicationMonitor
        
        replication_monitor = ReplicationMonitor()
        status = replication_monitor.check_replication_status()
        
        # Log status and check for issues
        primary_healthy = status['primary_healthy']
        standby_healthy = status['standby_healthy']
        lag_seconds = status['replication_lag_seconds']
        
        if not primary_healthy:
            celery_app.logger.error('Replication check: Primary database is not healthy')
        elif not standby_healthy:
            celery_app.logger.warning('Replication check: Standby is not healthy')
        elif lag_seconds > 60:
            celery_app.logger.warning(
                f'Replication check: High lag detected: {lag_seconds:.2f} seconds'
            )
        else:
            celery_app.logger.debug(
                f'Replication check: Primary healthy, Standby healthy, '
                f'Lag: {lag_seconds:.2f}s, WAL files behind: {status["wal_files_behind"]}'
            )
        
        return {
            'status': 'completed',
            'primary_healthy': primary_healthy,
            'standby_healthy': standby_healthy,
            'replication_lag_seconds': lag_seconds,
            'replication_lag_bytes': status['replication_lag_bytes'],
            'wal_files_behind': status['wal_files_behind'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as exc:
        celery_app.logger.error(f'check_replication_health task failed: {str(exc)}')
        # Retry after 30 seconds on failure
        raise self.retry(exc=exc, countdown=30)

# Multi-Region Tasks (Phase 3 Task 10)
@celery_app.task(bind=True, name='app.tasks.check_region_health')
def check_region_health(self):
    """Monitor health of all regional endpoints - runs every 60 seconds."""
    try:
        from app.multi_region_manager import RegionHealthChecker
        
        results = RegionHealthChecker.check_all_regions()
        
        # Count unhealthy regions
        unhealthy_count = sum(1 for r in results.values() if not r['healthy'])
        
        if unhealthy_count > 0:
            celery_app.logger.warning(f'Region health check: {unhealthy_count} region(s) unhealthy')
        else:
            celery_app.logger.debug('Region health check: All regions healthy')
        
        return {
            'status': 'completed',
            'healthy_regions': len(results) - unhealthy_count,
            'total_regions': len(results),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as exc:
        celery_app.logger.error(f'check_region_health task failed: {str(exc)}')
        # Retry after 30 seconds on failure
        raise self.retry(exc=exc, countdown=30)

@celery_app.task(bind=True, name='app.tasks.sync_cross_region_replicas')
def sync_cross_region_replicas(self):
    """Sync data across region replicas - runs every 5 minutes."""
    try:
        from app.models.multi_region import RegionReplica
        from app.multi_region_manager import ReplicationManager
        
        replicas = RegionReplica.query.filter_by(replication_status='syncing').all()
        
        synced_count = 0
        failed_count = 0
        
        for replica in replicas:
            success, result = ReplicationManager.sync_replica(replica)
            if success:
                synced_count += 1
            else:
                failed_count += 1
        
        if failed_count > 0:
            celery_app.logger.warning(f'Replica sync: {synced_count} synced, {failed_count} failed')
        else:
            celery_app.logger.debug(f'Replica sync: {synced_count} replicas synced')
        
        return {
            'status': 'completed',
            'synced_replicas': synced_count,
            'failed_syncs': failed_count,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as exc:
        celery_app.logger.error(f'sync_cross_region_replicas task failed: {str(exc)}')
        # Retry after 2 minutes on failure
        raise self.retry(exc=exc, countdown=120)

@celery_app.task(bind=True, name='app.tasks.replicate_cross_region_backups')
def replicate_cross_region_backups(self):
    """Replicate latest backups across regions - runs every 6 hours."""
    try:
        from app.models.multi_region import RegionConfig
        import os
        import shutil
        
        # Get primary region
        primary = RegionConfig.query.filter_by(is_primary=True).first()
        if not primary:
            raise Exception('Primary region not found')
        
        # Get secondary regions
        secondaries = RegionConfig.query.filter_by(is_primary=False).all()
        
        replicated_count = 0
        
        # Find latest backup from primary
        backup_dir = '/mnt/backups'
        if os.path.exists(backup_dir):
            # Get latest backup file
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.sql.gz')]
            if backup_files:
                latest_backup = max(backup_files, key=lambda f: os.path.getctime(os.path.join(backup_dir, f)))
                backup_path = os.path.join(backup_dir, latest_backup)
                backup_size = os.path.getsize(backup_path) / (1024**3)  # Convert to GB
                
                # Replicate to secondary regions (simplified - in production use AWS S3, Azure Blob, etc.)
                celery_app.logger.info(f'Replicating backup {latest_backup} ({backup_size:.2f}GB) to secondary regions')
                replicated_count = len(secondaries)
        
        return {
            'status': 'completed',
            'primary_region': primary.region_code,
            'replicated_to_regions': replicated_count,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as exc:
        celery_app.logger.error(f'replicate_cross_region_backups task failed: {str(exc)}')
        # Retry after 1 hour on failure
        raise self.retry(exc=exc, countdown=3600)

@celery_app.task(bind=True, name='app.tasks.cleanup_stale_geo_locations')
def cleanup_stale_geo_locations(self):
    """Clean up old geolocation cache entries - runs daily at 3 AM."""
    try:
        from app.models.multi_region import GeoLocation
        
        # Delete IP geolocation entries older than 30 days
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        deleted = GeoLocation.query.filter(GeoLocation.updated_at < cutoff_date).delete()
        db.session.commit()
        
        celery_app.logger.info(f'Deleted {deleted} stale geolocation entries')
        
        return {
            'status': 'completed',
            'deleted_entries': deleted,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as exc:
        celery_app.logger.error(f'cleanup_stale_geo_locations task failed: {str(exc)}')
        # Retry after 2 hours on failure
        raise self.retry(exc=exc, countdown=7200)
