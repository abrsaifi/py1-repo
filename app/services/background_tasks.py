"""
Background tasks and maintenance operations.
Includes automatic cleanup, backups, and optimization.
"""

import os
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Callable
import schedule


logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manage background tasks for maintenance and cleanup."""
    
    def __init__(self):
        self.tasks: dict = {}
        self.running = False
        self.thread = None
    
    def register_task(
        self,
        name: str,
        func: Callable,
        interval_hours: int = 1
    ) -> None:
        """
        Register a periodic background task.
        
        Args:
            name: Task identifier
            func: Callable to execute
            interval_hours: Interval between executions
        """
        self.tasks[name] = {
            'func': func,
            'interval': interval_hours,
            'last_run': None,
            'enabled': True
        }
        logger.info(f'Registered background task: {name}')
    
    def start(self) -> None:
        """Start background task execution."""
        if self.running:
            logger.warning('Background task manager already running')
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info('Background task manager started')
    
    def stop(self) -> None:
        """Stop background task execution."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info('Background task manager stopped')
    
    def _run_loop(self) -> None:
        """Main execution loop for background tasks."""
        while self.running:
            try:
                now = datetime.now()
                
                for task_name, task in self.tasks.items():
                    if not task['enabled']:
                        continue
                    
                    last_run = task['last_run']
                    if last_run is None or \
                       (now - last_run).total_seconds() >= task['interval'] * 3600:
                        
                        try:
                            logger.debug(f'Executing background task: {task_name}')
                            task['func']()
                            task['last_run'] = now
                            logger.info(f'Background task completed: {task_name}')
                        except Exception as e:
                            logger.error(
                                f'Background task failed: {task_name}',
                                exc_info=True
                            )
                
                # Sleep before next check
                time.sleep(60)
                
            except Exception as e:
                logger.error('Background task loop error', exc_info=True)
                time.sleep(60)


class MaintenanceTaskFactory:
    """Factory for creating standard maintenance tasks."""
    
    @staticmethod
    def cleanup_temp_files(
        temp_dir: str = None,
        max_age_hours: int = 24
    ) -> Callable:
        """Create temp file cleanup task."""
        if temp_dir is None:
            temp_dir = os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                'temp'
            )
        
        def cleanup():
            try:
                if not os.path.exists(temp_dir):
                    return
                
                now = time.time()
                cutoff = now - (max_age_hours * 3600)
                removed = 0
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        try:
                            if os.path.getmtime(file_path) < cutoff:
                                os.remove(file_path)
                                removed += 1
                        except:
                            pass
                
                if removed > 0:
                    logger.info(f'Cleanup: removed {removed} temp files')
                    
            except Exception as e:
                logger.error(f'Temp file cleanup failed: {str(e)}')
        
        return cleanup
    
    @staticmethod
    def backup_database(db_manager) -> Callable:
        """Create database backup task."""
        def backup():
            try:
                backup_path = db_manager.backup()
                if backup_path:
                    logger.info(f'Database backed up: {backup_path}')
            except Exception as e:
                logger.error(f'Database backup failed: {str(e)}')
        
        return backup
    
    @staticmethod
    def cleanup_old_backups(
        db_manager,
        max_age_days: int = 30
    ) -> Callable:
        """Create old backup cleanup task."""
        def cleanup():
            try:
                db_manager.cleanup_old_backups(days=max_age_days)
            except Exception as e:
                logger.error(f'Backup cleanup failed: {str(e)}')
        
        return cleanup
    
    @staticmethod
    def optimize_database(db_manager) -> Callable:
        """Create database optimization task."""
        def optimize():
            try:
                db_manager.optimize()
                logger.info('Database optimized')
            except Exception as e:
                logger.error(f'Database optimization failed: {str(e)}')
        
        return optimize


# Global task manager instance
_task_manager = BackgroundTaskManager()


def get_background_manager() -> BackgroundTaskManager:
    """Get global background task manager."""
    return _task_manager
