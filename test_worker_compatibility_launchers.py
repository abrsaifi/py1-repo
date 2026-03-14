"""Compatibility tests for legacy worker launcher scripts."""

from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parent


def _load_module(relative_path: str, module_name: str):
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_conversion_worker_dispatch_targets_expected_tasks(monkeypatch):
    cases = [
        (
            'workers/conversion-workers/pdf_worker.py',
            'pdf_worker_module',
            'PDFConversionWorker',
            {'conversion_id': 'pdf-123'},
            'app.tasks.process_pdf',
            'conversions',
        ),
        (
            'workers/conversion-workers/image_worker.py',
            'image_worker_module',
            'ImageConversionWorker',
            {'conversion_id': 'img-123'},
            'app.tasks.process_image',
            'conversions',
        ),
        (
            'workers/conversion-workers/doc_worker.py',
            'doc_worker_module',
            'DocumentConversionWorker',
            {'conversion_id': 'doc-123'},
            'app.tasks.convert_file',
            'conversions',
        ),
        (
            'workers/conversion-workers/compress_worker.py',
            'compress_worker_module',
            'CompressionWorker',
            {'operation_id': 'compress-123'},
            'app.tasks.long_running_operation',
            'maintenance',
        ),
    ]

    for relative_path, module_name, class_name, payload, expected_task, expected_queue in cases:
        module = _load_module(relative_path, module_name)
        worker = getattr(module, class_name)()
        captured = {}

        class FakeTaskResult:
            id = 'queued-task-id'

        def fake_submit(task_name, identifier, queue=expected_queue):
            captured['task_name'] = task_name
            captured['identifier'] = identifier
            captured['queue'] = queue
            return FakeTaskResult()

        monkeypatch.setattr(worker, '_submit_task', fake_submit)
        assert worker.process_job(payload) is True
        assert captured['task_name'] == expected_task
        assert captured['queue'] == expected_queue


def test_priority_worker_dispatches_to_critical_queue(monkeypatch):
    module = _load_module('workers/priority-worker/priority_queue.py', 'priority_worker_module')
    worker = module.PriorityWorker()
    captured = {}

    class FakeTaskResult:
        id = 'priority-task-id'

    def fake_submit(task_name, conversion_id, queue='critical'):
        captured['task_name'] = task_name
        captured['conversion_id'] = conversion_id
        captured['queue'] = queue
        return FakeTaskResult()

    monkeypatch.setattr(worker, '_submit_task', fake_submit)
    assert worker.process_job({'conversion_id': 'priority-123'}, module.UserTier.ENTERPRISE) is True
    assert captured == {
        'task_name': 'app.tasks.convert_file',
        'conversion_id': 'priority-123',
        'queue': 'critical',
    }


def test_cleanup_worker_queues_maintenance_tasks(monkeypatch):
    module = _load_module('workers/cleanup-worker/delete_expired_files.py', 'cleanup_worker_module')
    worker = module.CleanupWorker()

    class FakeTaskResult:
        id = 'cleanup-task-id'

    monkeypatch.setattr(worker, '_submit_task', lambda task_name, queue='maintenance': FakeTaskResult())

    stats = worker.cleanup_expired_files()
    assert stats['status'] == 'queued'
    assert stats['task_id'] == 'cleanup-task-id'
    assert stats['queue'] == 'maintenance'
    assert worker.cleanup_orphaned_files() == 1


def test_worker_start_commands_use_expected_queues(monkeypatch):
    cases = [
        ('workers/conversion-workers/pdf_worker.py', 'pdf_worker_start', 'PDFConversionWorker', 'conversions'),
        ('workers/cleanup-worker/delete_expired_files.py', 'cleanup_worker_start', 'CleanupWorker', 'maintenance'),
        ('workers/priority-worker/priority_queue.py', 'priority_worker_start', 'PriorityWorker', 'critical'),
    ]

    for relative_path, module_name, class_name, expected_queue in cases:
        module = _load_module(relative_path, module_name)
        worker = getattr(module, class_name)()
        captured = {}

        def fake_call(command, cwd=None):
            captured['command'] = command
            captured['cwd'] = cwd
            return 0

        monkeypatch.setattr(module.subprocess, 'call', fake_call)
        assert worker.start('ignored://queue-url') == 0
        assert '-A' in captured['command']
        assert 'app.celery_config' in captured['command']
        assert '-Q' in captured['command']
        assert expected_queue in captured['command']
        assert captured['cwd'] == str(module.ROOT_DIR)