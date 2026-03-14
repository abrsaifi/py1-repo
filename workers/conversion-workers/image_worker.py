"""Compatibility launcher for the Celery-backed image conversion queue."""

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class ImageConversionWorker:
    """Compatibility adapter for the package Celery image task."""

    def __init__(self):
        self.worker_id = os.getenv('WORKER_ID', 'image-worker-1')
        self.supported_formats = ['jpeg', 'png', 'webp', 'bmp', 'gif']

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

    def _submit_task(self, task_name, conversion_id, queue='conversions'):
        app = self._build_app()
        celery_app = getattr(app, 'celery', None)
        if celery_app is None:
            raise RuntimeError('Celery is not configured for this environment')
        with app.app_context():
            return celery_app.send_task(task_name, args=[conversion_id], queue=queue)

    def process_job(self, job):
        """
        Process an image conversion job from the queue
        
        Args:
            job: Job object containing image info and conversion params
        
        Returns:
            bool: Success status
        """
        try:
            conversion_id = self._get_job_value(job, 'conversion_id', self._get_job_value(job, 'id'))
            if conversion_id is None:
                raise ValueError('Missing conversion_id for image job')

            result = self._submit_task('app.tasks.process_image', conversion_id)
            logger.info(f"Queued image conversion: {conversion_id} as task {result.id}")
            return True
            
        except Exception as e:
            job_id = self._get_job_value(job, 'id', 'unknown')
            logger.error(f"Image conversion dispatch failed: {job_id} - {str(e)}")
            return False

    def start(self, queue_url):
        """Launch the project Celery worker bound to the conversions queue."""
        command = [
            sys.executable,
            '-m',
            'celery',
            '-A',
            'app.celery_config',
            'worker',
            '-Q',
            'conversions',
            '--hostname',
            f'{self.worker_id}@%h',
            '--loglevel=info',
        ]
        logger.info(f"Starting Celery conversions worker for {queue_url or 'configured broker'}")
        return subprocess.call(command, cwd=str(ROOT_DIR))


if __name__ == '__main__':
    worker = ImageConversionWorker()
    worker.start(os.getenv('QUEUE_URL'))
