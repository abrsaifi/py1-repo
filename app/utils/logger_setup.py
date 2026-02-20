"""
Enhanced structured logging system with multiple handlers and formats.
Supports console, file, and optional JSON logging for production.
"""

import os
import logging
import logging.handlers
from typing import Optional
import sys


class LoggerSetup:
    """Configure application logging with rotation and formatting."""
    
    @staticmethod
    def setup(
        app_name: str = 'docpro',
        level: str = 'INFO',
        log_file: Optional[str] = None,
        use_json: bool = False
    ) -> logging.Logger:
        """
        Setup logger with file and console handlers.
        
        Args:
            app_name: Application name for logger
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (if None, only console logging)
            use_json: Use JSON format for structured logging
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(app_name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(LoggerSetup._get_formatter(use_json=False))
        logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_file:
            os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=int(os.getenv('LOG_MAX_SIZE_MB', 50)) * 1024 * 1024,
                backupCount=int(os.getenv('LOG_BACKUP_COUNT', 5))
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(LoggerSetup._get_formatter(use_json=use_json))
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def _get_formatter(use_json: bool = False) -> logging.Formatter:
        """Get appropriate formatter."""
        if use_json:
            try:
                from pythonjsonlogger import jsonlogger
                return jsonlogger.JsonFormatter(
                    '%(timestamp)s %(level)s %(name)s %(message)s'
                )
            except ImportError:
                pass
        
        # Default format
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def get_logger(name: str = 'docpro') -> logging.Logger:
    """Get or create a logger instance."""
    import os
    from logging import INFO
    
    level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/app.log')
    use_json = os.getenv('LOG_FORMAT', 'standard').lower() == 'json'
    
    return LoggerSetup.setup(
        app_name=name,
        level=level,
        log_file=log_file,
        use_json=use_json
    )
