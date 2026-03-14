"""Compatibility launcher for the Celery-backed maintenance queue."""

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class CompressionWorker:
    """Compatibility adapter for long-running compression operations."""

    def __init__(self):
        self.worker_id = os.getenv('WORKER_ID', 'compress-worker-1')

    @staticmethod
    def _get_job_value(job, key, default=None):
        if isinstance(job, dict):
            return job.get(key, default)
        return getattr(job, key, default)

    @staticmethod
    def _build_app():
        from app import create_app

        return create_app({
            'ENABLE_BACKGROUND_TASKS': False,
            'LOG_LEVEL': 'WARNING',
        })

    def _submit_task(self, task_name, operation_id, queue='maintenance'):
        app = self._build_app()
        celery_app = getattr(app, 'celery', None)
        if celery_app is None:
            raise RuntimeError('Celery is not configured for this environment')
        with app.app_context():
            return celery_app.send_task(task_name, args=[operation_id], queue=queue)
        
    def process_job(self, job):
        """
        Process a compression job from the queue
        
        Args:
            job: Job object containing file info and compression params
        
        Returns:
            bool: Success status
        """
        try:
            operation_id = self._get_job_value(job, 'operation_id', self._get_job_value(job, 'id'))
            if operation_id is None:
                raise ValueError('Missing operation_id for compression job')

            result = self._submit_task('app.tasks.long_running_operation', operation_id)
            logger.info(f"Queued compression job: {operation_id} as task {result.id}")
            return True
            
        except Exception as e:
            job_id = self._get_job_value(job, 'id', 'unknown')
            logger.error(f"Compression dispatch failed: {job_id} - {str(e)}")
            return False

    def start(self, queue_url):
        """Launch the project Celery worker bound to the maintenance queue."""
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
        logger.info(f"Starting Celery maintenance worker for {queue_url or 'configured broker'}")
        return subprocess.call(command, cwd=str(ROOT_DIR))


if __name__ == '__main__':
    worker = CompressionWorker()
    worker.start(os.getenv('QUEUE_URL'))
