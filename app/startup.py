"""Application startup tasks and initialization for background processes."""

import os
import logging
from app.services.database import DatabaseManager
from app.services.background_tasks import (
    get_background_manager,
    MaintenanceTaskFactory
)

logger = logging.getLogger(__name__)


def init_background_tasks():
    """Initialize background tasks for maintenance.
    
    Sets up:
    - Daily database backups
    - Weekly backup cleanup
    - Weekly database optimization
    - Hourly temp file cleanup
    """
    
    try:
        manager = get_background_manager()
        logger.info('Background task manager retrieved')
        
        # Database file paths
        history_db = 'conversion_history.db'
        
        if not os.path.exists(history_db):
            logger.warning(f'Database not found: {history_db}')
            return
        
        # Create database manager
        db = DatabaseManager(history_db)
        logger.info(f'Database manager initialized: {history_db}')
        
        # Register backup task (every 24 hours)
        def backup_task():
            try:
                logger.info('Starting daily database backup')
                backup_path = db.backup()
                logger.info(f'Daily database backup completed: {backup_path}')
            except Exception as e:
                logger.error(f'Daily backup failed: {str(e)}', exc_info=True)
        
        manager.register_task(
            'daily_backup',
            backup_task,
            interval_hours=24
        )
        logger.info('Registered: Daily database backup (every 24 hours)')
        
        # Register cleanup task (every 7 days)
        def cleanup_task():
            try:
                logger.info('Starting backup cleanup')
                # Remove backups older than 30 days
                backups_dir = 'backups'
                if os.path.exists(backups_dir):
                    import time
                    current_time = time.time()
                    max_age = 30 * 24 * 60 * 60  # 30 days in seconds
                    removed = 0
                    
                    for filename in os.listdir(backups_dir):
                        filepath = os.path.join(backups_dir, filename)
                        if os.path.isfile(filepath):
                            file_age = current_time - os.path.getmtime(filepath)
                            if file_age > max_age:
                                os.remove(filepath)
                                removed += 1
                    
                    logger.info(f'Backup cleanup completed: {removed} old backups removed')
            except Exception as e:
                logger.error(f'Backup cleanup failed: {str(e)}', exc_info=True)
        
        manager.register_task(
            'weekly_backup_cleanup',
            cleanup_task,
            interval_hours=24*7
        )
        logger.info('Registered: Weekly backup cleanup (every 7 days)')
        
        # Register optimization task (every 7 days)
        def optimize_task():
            try:
                logger.info('Starting database optimization')
                db.optimize()
                logger.info('Database optimization completed')
            except Exception as e:
                logger.error(f'Database optimization failed: {str(e)}', exc_info=True)
        
        manager.register_task(
            'weekly_optimization',
            optimize_task,
            interval_hours=24*7
        )
        logger.info('Registered: Weekly database optimization (every 7 days)')
        
        # Register temp cleanup task (every hour)
        def temp_cleanup_task():
            try:
                logger.info('Starting temp file cleanup')
                temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
                if os.path.exists(temp_dir):
                    import time
                    current_time = time.time()
                    max_age = 24 * 60 * 60  # 24 hours in seconds
                    removed = 0
                    
                    for filename in os.listdir(temp_dir):
                        filepath = os.path.join(temp_dir, filename)
                        if os.path.isfile(filepath):
                            file_age = current_time - os.path.getmtime(filepath)
                            if file_age > max_age:
                                try:
                                    os.remove(filepath)
                                    removed += 1
                                except:
                                    pass  # Can't remove, skip
                    
                    logger.info(f'Temp cleanup completed: {removed} old files removed')
            except Exception as e:
                logger.error(f'Temp cleanup failed: {str(e)}', exc_info=True)
        
        manager.register_task(
            'hourly_temp_cleanup',
            temp_cleanup_task,
            interval_hours=1
        )
        logger.info('Registered: Hourly temp file cleanup (every hour)')
        
        # Start the manager
        manager.start()
        logger.info('Background task manager started successfully')
        
    except Exception as e:
        logger.error(f'Failed to initialize background tasks: {str(e)}', exc_info=True)


def init_app(app):
    """Initialize application (called after app creation).
    
    Sets up:
    - Background task scheduler
    - Database initialization
    - Logging configuration
    """
    
    # Setup background tasks
    init_background_tasks()
    
    logger.info('Application initialization complete')


def create_task_manager():
    """Create and return task manager for external use."""
    try:
        manager = get_background_manager()
        logger.info('Task manager created')
        return manager
    except Exception as e:
        logger.error(f'Failed to create task manager: {str(e)}')
        return None
