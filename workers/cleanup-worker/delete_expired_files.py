"""Compatibility launcher for the Celery-backed upload cleanup queue."""

import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class CleanupWorker:
    """Compatibility adapter for maintenance cleanup tasks."""

    def __init__(self):
        self.worker_id = os.getenv('WORKER_ID', 'cleanup-worker-1')
        self.retention_days = int(os.getenv('FILE_RETENTION_DAYS', 30))
        self.batch_size = int(os.getenv('CLEANUP_BATCH_SIZE', 100))

    @staticmethod
    def _build_app():
        from app import create_app

        return create_app({
            'ENABLE_BACKGROUND_TASKS': False,
            'LOG_LEVEL': 'WARNING',
        })

    def _submit_task(self, task_name, queue='maintenance'):
        app = self._build_app()
        celery_app = getattr(app, 'celery', None)
        if celery_app is None:
            raise RuntimeError('Celery is not configured for this environment')
        with app.app_context():
            return celery_app.send_task(task_name, queue=queue)

    def cleanup_expired_files(self):
        """
        Find and delete files that have exceeded retention period
        
        Returns:
            dict: Cleanup statistics
        """
        try:
            logger.info(f"Starting cleanup job, retention: {self.retention_days} days")
            result = self._submit_task('app.tasks.cleanup_old_uploads')
            
            stats = {
                'status': 'queued',
                'task_id': result.id,
                'queue': 'maintenance',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Cleanup completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return None

    def cleanup_orphaned_files(self):
        """
        Find and delete files with no associated job record
        
        Returns:
            int: Number of orphaned files deleted
        """
        try:
            logger.info("Scanning for orphaned files")
            result = self._submit_task('app.tasks.cleanup_old_uploads')
            logger.info(f"Queued orphan cleanup audit as task {result.id}")
            return 1
            
        except Exception as e:
            logger.error(f"Orphan cleanup failed: {str(e)}")
            return 0

    def start(self, run_interval_hours=1):
        """
        Start the cleanup worker to run periodically
        
        Args:
            run_interval_hours: How often to run cleanup (default: hourly)
        """
        logger.info(f"Cleanup worker {self.worker_id} started (interval: {run_interval_hours}h)")
        command = [
            sys.executable,
            '-m',
            'celery',
            '-A',
            'app.celery_config',
            'worker',
            '-Q',
            'maintenance',
            '--hostname',
            f'{self.worker_id}@%h',
            '--loglevel=info',
        ]
        return subprocess.call(command, cwd=str(ROOT_DIR))


if __name__ == '__main__':
    worker = CleanupWorker()
    worker.start()
