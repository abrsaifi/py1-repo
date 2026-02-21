"""
Enhanced configuration management with environment-aware settings.
Supports development, testing, and production environments.
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration - shared across all environments."""
    
    # Flask Framework
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE_MB', 100)) * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,jpg,jpeg,png,docx,xlsx,pptx').split(','))
    UPLOAD_CHUNKS_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp', 'uploads')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///docpro_database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_BACKUP_ENABLED = os.getenv('DATABASE_BACKUP_ENABLED', 'true').lower() == 'true'
    DATABASE_BACKUP_DAYS = int(os.getenv('DATABASE_BACKUP_DAYS', 7))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_MAX_SIZE_MB = int(os.getenv('LOG_MAX_SIZE_MB', 50))
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    
    # Performance
    CONVERSION_TIMEOUT = int(os.getenv('CONVERSION_TIMEOUT_SECONDS', 300))
    TEMP_FILES_CLEANUP_INTERVAL = int(os.getenv('TEMP_FILES_CLEANUP_INTERVAL_HOURS', 1)) * 3600
    TEMP_FILES_MAX_AGE = int(os.getenv('TEMP_FILES_MAX_AGE_HOURS', 24)) * 3600
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATE_LIMIT_REQUESTS', '100/1hour')
    
    # CORS
    CORS_ENABLED = os.getenv('CORS_ENABLED', 'true').lower() == 'true'
    CORS_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # API
    API_VERSION = os.getenv('API_VERSION', 'v1')
    API_DOCUMENTATION_ENABLED = os.getenv('API_DOCUMENTATION_ENABLED', 'true').lower() == 'true'
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT_SECONDS', 300))
    
    # Monitoring
    MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'true').lower() == 'true'
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL_SECONDS', 60))
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', 8000))
    
    # Features
    FEATURES = {
        'watermarking': os.getenv('FEATURE_WATERMARKING', 'true').lower() == 'true',
        'ocr': os.getenv('FEATURE_OCR', 'true').lower() == 'true',
        'batch_processing': os.getenv('FEATURE_BATCH_PROCESSING', 'true').lower() == 'true',
        'webhooks': os.getenv('FEATURE_WEBHOOK_CALLBACKS', 'false').lower() == 'true',
        'analytics': os.getenv('FEATURE_ADVANCED_ANALYTICS', 'true').lower() == 'true',
        'audit_log': os.getenv('FEATURE_AUDIT_LOG', 'true').lower() == 'true',
    }


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    # Ensure secret key is set from environment in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable must be set in production!')


def get_config(env=None):
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Default Config
Config = get_config()
