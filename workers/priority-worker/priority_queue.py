"""Compatibility launcher for the Celery-backed critical queue."""

import logging
import os
import subprocess
import sys
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class UserTier(Enum):
    """User subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class PriorityWorker:
    """Compatibility adapter for premium jobs routed to the critical queue."""

    def __init__(self):
        self.worker_id = os.getenv('WORKER_ID', 'priority-worker-1')
        self.tier_priority = {
            UserTier.FREE: 4,
            UserTier.BASIC: 3,
            UserTier.PRO: 2,
            UserTier.ENTERPRISE: 1  # Lowest number = highest priority
        }

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

    def _submit_task(self, task_name, conversion_id, queue='critical'):
        app = self._build_app()
        celery_app = getattr(app, 'celery', None)
        if celery_app is None:
            raise RuntimeError('Celery is not configured for this environment')
        with app.app_context():
            return celery_app.send_task(task_name, args=[conversion_id], queue=queue)

    def process_job(self, job, user_tier):
        """
        Process a job with priority based on user tier
        
        Args:
            job: Job object to process
            user_tier: User's subscription tier
        
        Returns:
            bool: Success status
        """
        try:
            priority = self.tier_priority.get(user_tier, 4)
            conversion_id = self._get_job_value(job, 'conversion_id', self._get_job_value(job, 'id'))
            if conversion_id is None:
                raise ValueError('Missing conversion_id for priority job')

            result = self._submit_task('app.tasks.convert_file', conversion_id)
            logger.info(
                f"Queued priority job: {conversion_id}, tier: {user_tier.value}, priority: {priority}, task: {result.id}"
            )
            return True
            
        except Exception as e:
            job_id = self._get_job_value(job, 'id', 'unknown')
            logger.error(f"Priority job dispatch failed: {job_id} - {str(e)}")
            return False

    def get_processing_time_sla(self, user_tier):
        """
        Get expected processing time SLA for user tier
        
        Args:
            user_tier: User's subscription tier
        
        Returns:
            dict: SLA details (max_wait_minutes, max_process_minutes)
        """
        slas = {
            UserTier.FREE: {'max_wait': 30, 'max_process': 60},
            UserTier.BASIC: {'max_wait': 10, 'max_process': 30},
            UserTier.PRO: {'max_wait': 2, 'max_process': 10},
            UserTier.ENTERPRISE: {'max_wait': 0.5, 'max_process': 5},
        }
        return slas.get(user_tier, slas[UserTier.FREE])

    def start(self, queue_url):
        """Launch the project Celery worker bound to the critical queue."""
        command = [
            sys.executable,
            '-m',
            'celery',
            '-A',
            'app.celery_config',
            'worker',
            '-Q',
            'critical',
            '--hostname',
            f'{self.worker_id}@%h',
            '--loglevel=info',
        ]
        logger.info(f"Starting Celery critical worker for {queue_url or 'configured broker'}")
        return subprocess.call(command, cwd=str(ROOT_DIR))


if __name__ == '__main__':
    worker = PriorityWorker()
    worker.start(os.getenv('PRIORITY_QUEUE_URL'))
