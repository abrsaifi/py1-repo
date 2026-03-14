"""Celery configuration for background task processing."""
import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# Get environment
ENV = os.getenv('FLASK_ENV', 'development')

def make_celery(app):
    """Create and configure Celery instance."""
    broker_url = app.config.get('CELERY_BROKER_URL') or os.getenv('CELERY_BROKER_URL', 'memory://')
    result_backend = app.config.get('CELERY_RESULT_BACKEND') or os.getenv('CELERY_RESULT_BACKEND', 'cache+memory://')
    
    celery = Celery(
        app.import_name,
        backend=result_backend,
        broker=broker_url,
        include=['app.tasks']
    )
    
    # Configuration
    celery.conf.update(
        # Task settings
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        
        # Task execution settings
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes hard limit
        task_soft_time_limit=25 * 60,  # 25 minutes soft limit
        
        # Result backend settings
        result_expires=3600,  # Results expire after 1 hour
        result_backend_transport_options={
            'master_name': 'mymaster',
            'retry_on_timeout': True
        },
        
        # Worker settings
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=False,
        
        # Retries
        task_autoretry_for=(Exception,),
        task_max_retries=3,
        task_default_retry_delay=60,
        
        # Beat Schedule (Periodic Tasks)
        beat_schedule={
            'cleanup-old-uploads': {
                'task': 'app.tasks.cleanup_old_uploads',
                'schedule': timedelta(hours=1),
                'options': {'queue': 'default'}
            },
            'update-conversion-stats': {
                'task': 'app.tasks.update_conversion_stats',
                'schedule': timedelta(minutes=5),
                'options': {'queue': 'default'}
            },
            'send-daily-reports': {
                'task': 'app.tasks.send_daily_reports',
                'schedule': timedelta(days=1),
                'options': {'queue': 'default'}
            },
            # Phase 3 Task 9: Disaster Recovery Tasks
            'backup-database-full': {
                'task': 'app.tasks.backup_database_full',
                'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
                'options': {'queue': 'critical'}
            },
            'verify-latest-backup': {
                'task': 'app.tasks.verify_latest_backup',
                'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3:00 AM
                'options': {'queue': 'critical'}
            },
            'cleanup-old-backups': {
                'task': 'app.tasks.cleanup_old_backups',
                'schedule': crontab(hour=4, minute=0, day_of_month=1),  # 1st of month at 4:00 AM
                'options': {'queue': 'maintenance', 'kwargs': {'retention_days': 30}}
            },
            'replication-health-check': {
                'task': 'app.tasks.check_replication_health',
                'schedule': timedelta(minutes=5),  # Every 5 minutes
                'options': {'queue': 'critical'}
            },
            # Phase 3 Task 10: Multi-Region Tasks
            'region-health-check': {
                'task': 'app.tasks.check_region_health',
                'schedule': timedelta(minutes=1),  # Every minute
                'options': {'queue': 'critical'}
            },
            'sync-cross-region-replicas': {
                'task': 'app.tasks.sync_cross_region_replicas',
                'schedule': timedelta(minutes=5),  # Every 5 minutes
                'options': {'queue': 'critical'}
            },
            'replicate-cross-region-backups': {
                'task': 'app.tasks.replicate_cross_region_backups',
                'schedule': timedelta(hours=6),  # Every 6 hours
                'options': {'queue': 'maintenance'}
            },
            'cleanup-stale-geo-locations': {
                'task': 'app.tasks.cleanup_stale_geo_locations',
                'schedule': crontab(hour=3, minute=0),  # Daily at 3:00 AM
                'options': {'queue': 'maintenance'}
            },
        },
        
        # Routing
        task_routes={
            'app.tasks.convert_file': {'queue': 'conversions'},
            'app.tasks.process_image': {'queue': 'conversions'},
            'app.tasks.process_pdf': {'queue': 'conversions'},
            'app.tasks.send_email': {'queue': 'emails'},
            'app.tasks.cleanup_old_uploads': {'queue': 'maintenance'},
            # Phase 3 Task 9: Disaster Recovery routing
            'app.tasks.backup_database_full': {'queue': 'critical'},
            'app.tasks.verify_latest_backup': {'queue': 'critical'},
            'app.tasks.cleanup_old_backups': {'queue': 'maintenance'},
            'app.tasks.check_replication_health': {'queue': 'critical'},
            # Phase 3 Task 10: Multi-Region routing
            'app.tasks.check_region_health': {'queue': 'critical'},
            'app.tasks.sync_cross_region_replicas': {'queue': 'critical'},
            'app.tasks.replicate_cross_region_backups': {'queue': 'maintenance'},
            'app.tasks.cleanup_stale_geo_locations': {'queue': 'maintenance'},
        }
    )
    
    class ContextTask(celery.Task):
        """Celery task with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
