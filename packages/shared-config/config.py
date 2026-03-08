"""
Shared Configuration Package
Centralized configuration management for all microservices.
"""

import os
from typing import Optional


class BaseConfig:
    """Base configuration for all services"""
    
    # Environment
    ENV = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Database
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = int(os.getenv('DATABASE_PORT', 5432))
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'file_converter')
    DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'password')
    
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    
    # Redis/Cache
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Storage
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')  # local, s3, gcs
    STORAGE_PATH = os.getenv('STORAGE_PATH', '/tmp/conversions')
    
    # AWS S3 (if using S3 storage)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', 24))
    
    # Service Configuration
    SERVICE_NAME = 'file-converter-service'
    SERVICE_VERSION = '1.0.0'
    
    # Queue Configuration
    QUEUE_TYPE = os.getenv('QUEUE_TYPE', 'redis')  # redis, rabbitmq, sqs
    QUEUE_URL = os.getenv('QUEUE_URL', 'redis://localhost:6379/1')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File Upload
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 100))
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt',
        'png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif', 'txt', 'csv', 'html'
    }
    
    # File Retention
    FILE_RETENTION_DAYS = int(os.getenv('FILE_RETENTION_DAYS', 30))
    
    # Worker Configuration
    WORKER_CONCURRENCY = int(os.getenv('WORKER_CONCURRENCY', 4))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    # API Configuration
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100/minute')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    ENV = 'development'
    DEBUG = True
    DATABASE_NAME = 'file_converter_dev'


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    ENV = 'production'
    DEBUG = False
    # Production settings will override from environment variables


class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    ENV = 'testing'
    DEBUG = True
    DATABASE_NAME = 'file_converter_test'
    TESTING = True


def get_config(env: Optional[str] = None) -> BaseConfig:
    """Get configuration based on environment"""
    env = env or os.getenv('ENVIRONMENT', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    return configs.get(env, DevelopmentConfig)()


# Config __init__
__all__ = [
    'BaseConfig',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig',
    'get_config',
]
