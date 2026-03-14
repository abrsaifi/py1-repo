import os
import tempfile


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'docpro-dev-secret-key-change-me-2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 60 * 60 * 24))
    ENABLE_BACKGROUND_TASKS = os.environ.get('ENABLE_BACKGROUND_TASKS', 'True').lower() == 'true'
    SCHEMA_BOOTSTRAP_ENABLED = os.environ.get('SCHEMA_BOOTSTRAP_ENABLED', 'True').lower() == 'true'
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
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR') or os.path.join(os.getcwd(), 'logs')
    
    # Authentication
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 60))

    # Billing provider sync
    BILLING_PROVIDER_WEBHOOK_SECRET = os.environ.get('BILLING_PROVIDER_WEBHOOK_SECRET')
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 100))

    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or ('RedisCache' if os.environ.get('CACHE_REDIS_URL') else 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or os.environ.get('REDIS_URL')

    # Background task broker
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'memory://')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'cache+memory://')

    HISTORY_DB = os.environ.get('HISTORY_DB') or os.path.join(os.getcwd(), 'conversion_history.db')
