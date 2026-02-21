import os
import tempfile


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))
    UPLOAD_API_KEY = os.environ.get('UPLOAD_API_KEY')

    # Upload storage defaults
    UPLOAD_CHUNKS_DIR = os.environ.get('UPLOAD_CHUNKS_DIR') or os.path.join(os.getenv('TMP', tempfile.gettempdir()), 'docpro_uploads')
    UPLOAD_MAX_FILE_SIZE = int(os.environ.get('UPLOAD_MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100 MB
    UPLOAD_CLEANUP_RETENTION = int(os.environ.get('UPLOAD_CLEANUP_RETENTION', 24 * 3600))
    UPLOAD_CLEANUP_INTERVAL = int(os.environ.get('UPLOAD_CLEANUP_INTERVAL', 3600))

    # File validation
    MAX_FILE_SIZE_MB = int(os.environ.get('MAX_FILE_SIZE_MB', 100))
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(os.getcwd(), 'docpro_database.db')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR') or os.path.join(os.getcwd(), 'logs')
    
    # Authentication
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 60))
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 100))

    HISTORY_DB = os.environ.get('HISTORY_DB') or os.path.join(os.getcwd(), 'conversion_history.db')
