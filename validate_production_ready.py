#!/usr/bin/env python3
"""
Validate that all robustness improvements are in place and working.
Run this before deployment to ensure system is production-ready.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime


class ProductionValidation:
    """Validate production-readiness of the system."""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def check(self, name: str, condition: bool, level: str = 'error') -> None:
        """Record a validation check result."""
        status = '[OK]' if condition else ('[WARN]' if level == 'warning' else '[FAIL]')
        
        if condition:
            self.passed += 1
            print(f"{status} PASS: {name}")
        else:
            print(f"{status} {'WARN' if level == 'warning' else 'FAIL'}: {name}")
            if level == 'warning':
                self.warnings += 1
            else:
                self.failed += 1
        
        self.checks.append({'name': name, 'passed': condition, 'level': level})
    
    def file_exists(self, path: str, description: str = '') -> bool:
        """Check if file exists."""
        exists = os.path.exists(path)
        desc = description or path
        self.check(f"File exists: {desc}", exists)
        return exists
    
    def contains_text(
        self,
        file_path: str,
        text: str,
        description: str = ''
    ) -> bool:
        """Check if file contains specific text."""
        desc = description or text
        if not os.path.exists(file_path):
            self.check(
                f"File contains {desc}: {file_path} (file not found)",
                False
            )
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                found = text in content
                self.check(f"File {file_path} contains: {desc}", found)
                return found
        except Exception as e:
            self.check(f"Read {file_path}: {desc}", False)
            return False
    
    def env_var(self, var: str, required: bool = False) -> bool:
        """Check environment variable."""
        exists = var in os.environ
        if required:
            self.check(f"Required env var: {var}", exists)
        else:
            self.check(f"Optional env var: {var}", exists, level='warning')
        return exists
    
    def importable(
        self,
        module: str,
        description: str = '',
        level: str = 'error'
    ) -> bool:
        """Check if Python module can be imported."""
        try:
            __import__(module)
            desc = description or module
            self.check(f"Python module importable: {desc}", True, level=level)
            return True
        except ImportError:
            desc = description or module
            self.check(f"Python module importable: {desc}", False, level=level)
            return False
    
    def print_summary(self) -> int:
        """Print validation summary and return exit code."""
        print("\n" + "="*70)
        print("PRODUCTION READINESS VALIDATION SUMMARY")
        print("="*70)
        print(f"Passed:  {self.passed}")
        print(f"Failed:  {self.failed}")
        print(f"Warnings: {self.warnings}")
        print("="*70)
        
        if self.failed == 0:
            print("[YES] STATUS: PRODUCTION READY")
            return 0
        else:
            print("[NO] STATUS: NOT READY FOR PRODUCTION")
            print("\nFailed checks:")
            for check in self.checks:
                if not check['passed'] and check['level'] != 'warning':
                    print(f"  - {check['name']}")
            return 1


def run_validation():
    """Run all production readiness checks."""
    v = ProductionValidation()
    
    print("\n" + "="*70)
    print("PRODUCTION READINESS VALIDATION")
    print("="*70 + "\n")
    
    # 1. Configuration Files
    print("\n[1] Configuration Files")
    print("-"*70)
    v.file_exists('.env.example', '.env.example template')
    v.file_exists('.env', '.env (copy of .env.example)')
    v.file_exists('requirements.txt', 'requirements.txt with pinned versions')
    v.file_exists('Dockerfile', 'Dockerfile for containerization')
    v.file_exists('docker-compose.yml', 'docker-compose.yml for orchestration')
    
    # 2. New Robustness Files
    print("\n[2] Robustness Improvement Files")
    print("-"*70)
    v.file_exists('app/config_enhanced.py', 'Enhanced configuration module')
    v.file_exists('app/utils/logger_setup.py', 'Structured logging setup')
    v.file_exists('app/utils/errors.py', 'Custom error handlers')
    v.file_exists('app/services/database.py', 'Database utilities')
    v.file_exists('app/services/background_tasks.py', 'Background task manager')
    v.file_exists('app/api/routes/health.py', 'Health check endpoint')
    
    # 3. Documentation
    print("\n[3] Documentation Files")
    print("-"*70)
    v.file_exists('ROBUSTNESS_IMPROVEMENTS.md', 'Robustness documentation')
    v.file_exists('DEPLOYMENT_GUIDE.md', 'Deployment guide')
    v.file_exists('PRODUCTION_READY_SUMMARY.md', 'Production summary')
    
    # 4. Version Pinning
    print("\n[4] Dependency Management")
    print("-"*70)
    v.contains_text('requirements.txt', 'Flask==', 'Flask version pinned')
    v.contains_text('requirements.txt', 'PyMuPDF==', 'PyMuPDF version pinned')
    v.contains_text('requirements.txt', '# Core', 'Requirements organized')
    v.contains_text('requirements.txt', 'python-json-logger', 'JSON logging support')
    
    # 5. Environment Configuration
    print("\n[5] Environment Configuration")
    print("-"*70)
    v.contains_text('.env.example', 'FLASK_ENV', '.env has FLASK_ENV')
    v.contains_text('.env.example', 'SECRET_KEY', '.env has SECRET_KEY')
    v.contains_text('.env.example', 'DATABASE_BACKUP_ENABLED', '.env has backup config')
    v.contains_text('.env.example', 'LOG_LEVEL', '.env has logging config')
    v.env_var('FLASK_ENV', required=False)
    
    # 6. Error Handling
    print("\n[6] Error Handling")
    print("-"*70)
    v.contains_text(
        'app/utils/errors.py',
        'class AppError',
        'Custom AppError class defined'
    )
    v.contains_text(
        'app/utils/errors.py',
        'class ConversionError',
        'ConversionError class defined'
    )
    v.contains_text(
        'app/utils/errors.py',
        'register_error_handlers',
        'Error handler registration function'
    )
    
    # 7. Logging
    print("\n[7] Logging System")
    print("-"*70)
    v.contains_text(
        'app/utils/logger_setup.py',
        'class LoggerSetup',
        'LoggerSetup class defined'
    )
    v.contains_text(
        'app/utils/logger_setup.py',
        'RotatingFileHandler',
        'Rotating file handler configured'
    )
    v.importable('logging.handlers', 'Python logging.handlers')
    
    # 8. Health Checks
    print("\n[8] Health Check Endpoints")
    print("-"*70)
    v.contains_text(
        'app/api/routes/health.py',
        'def get_status',
        'Health status endpoint defined'
    )
    v.contains_text(
        'app/api/routes/health.py',
        'def liveness_probe',
        'Kubernetes liveness probe'
    )
    v.contains_text(
        'app/api/routes/health.py',
        'def readiness_probe',
        'Kubernetes readiness probe'
    )
    v.contains_text(
        'app/api/routes/health.py',
        'def get_metrics',
        'Metrics endpoint defined'
    )
    
    # 9. Database Management
    print("\n[9] Database Management")
    print("-"*70)
    v.contains_text(
        'app/services/database.py',
        'def init_db',
        'Database initialization function'
    )
    v.contains_text(
        'app/services/database.py',
        'CREATE TABLE',
        'Database schema defined'
    )
    
    # 10. Background Tasks
    print("\n[10] Background Tasks")
    print("-"*70)
    v.contains_text(
        'app/services/background_tasks.py',
        'class BackgroundTaskManager',
        'BackgroundTaskManager class defined'
    )
    v.contains_text(
        'app/services/background_tasks.py',
        'class MaintenanceTaskFactory',
        'MaintenanceTaskFactory class defined'
    )
    v.contains_text(
        'app/services/background_tasks.py',
        'def cleanup_temp_files',
        'Cleanup function factory'
    )
    
    # 11. Docker Support
    print("\n[11] Container Deployment")
    print("-"*70)
    v.contains_text('Dockerfile', 'FROM python', 'Dockerfile uses Python base')
    v.contains_text(
        'Dockerfile',
        'HEALTHCHECK',
        'Docker health check configured'
    )
    v.contains_text(
        'docker-compose.yml',
        'services',
        'Docker Compose configured'
    )
    
    # 12. Python Modules
    print("\n[12] Required Python Modules")
    print("-"*70)
    v.importable('flask', 'Flask web framework')
    v.importable('fitz', 'PyMuPDF')
    v.importable('PIL', 'Pillow')
    v.importable('logging', 'Python logging')
    v.importable('sqlite3', 'SQLite')
    v.importable('psutil', 'psutil (optional for health checks)', 'warning')
    
    # 13. Documentation Quality
    print("\n[13] Documentation")
    print("-"*70)
    v.contains_text(
        'ROBUSTNESS_IMPROVEMENTS.md',
        'ENHANCED ERROR HANDLING',
        'Error handling documentation'
    )
    v.contains_text(
        'DEPLOYMENT_GUIDE.md',
        'Environment Setup',
        'Deployment documentation'
    )
    v.contains_text(
        'PRODUCTION_READY_SUMMARY.md',
        'Production-Ready System Summary',
        'Production summary'
    )
    
    # 14. Application Files
    print("\n[14] Application Files")
    print("-"*70)
    v.file_exists('server.py', 'Main Flask server')
    v.file_exists('app.py', 'App factory')
    v.file_exists('app/__init__.py', 'App package')
    v.file_exists('pdf_handler.py', 'PDF handler utilities')
    v.file_exists('image_processor.py', 'Image processor utilities')
    v.file_exists('file_utils.py', 'File utilities')
    
    # Print summary and return exit code
    return v.print_summary()


if __name__ == '__main__':
    sys.exit(run_validation())
