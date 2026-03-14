"""Comprehensive logging and monitoring system"""
import os
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

# Setup logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs"""
    def format(self, record):
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)

def setup_logging():
    """Setup comprehensive logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    operations_log = Path(os.getenv('LOG_OPERATIONS_FILE', str(LOGS_DIR / 'operations.log')))
    operations_log.parent.mkdir(exist_ok=True)
    errors_log = Path(os.getenv('LOG_ERRORS_FILE', str(LOGS_DIR / 'errors.log')))
    errors_log.parent.mkdir(exist_ok=True)

    # File handler - all logs
    file_handler = logging.handlers.RotatingFileHandler(
        operations_log,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        delay=True,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # File handler - errors only
    error_handler = logging.handlers.RotatingFileHandler(
        errors_log,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        delay=True,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name):
    """Get logger instance"""
    return logging.getLogger(name)

class OperationLogger:
    """Log operations with metadata"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.logger = get_logger(operation_name)
        self.start_time = datetime.now()
    
    def log_start(self, **metadata):
        """Log operation start"""
        self.logger.info(f"Operation started", extra={'extra_data': {'metadata': metadata}})
        self.start_time = datetime.now()
    
    def log_success(self, **metadata):
        """Log operation success"""
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.info(
            f"Operation completed successfully",
            extra={'extra_data': {'duration_seconds': duration, 'metadata': metadata}}
        )
    
    def log_error(self, error, **metadata):
        """Log operation error"""
        duration = (datetime.now() - self.start_time).total_seconds()
        self.logger.error(
            f"Operation failed: {str(error)}",
            extra={'extra_data': {'duration_seconds': duration, 'error': str(error), 'metadata': metadata}},
            exc_info=True
        )
    
    def log_info(self, message, **metadata):
        """Log operation info"""
        self.logger.info(message, extra={'extra_data': metadata})

class AuditLogger:
    """Log user actions for audit trail"""
    
    audit_logger = logging.getLogger('audit')
    
    @classmethod
    def log_action(cls, user_id, action, resource, status='success', details=None):
        """Log user action"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'status': status,
            'details': details or {}
        }
        cls.audit_logger.info(
            f"User action: {action} on {resource}",
            extra={'extra_data': log_entry}
        )

# Initialize logging on module import
setup_logging()
