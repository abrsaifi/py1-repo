"""Environment and secrets configuration management."""
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

class SecretConfig:
    """Centralized secrets management."""
    
    @staticmethod
    def get_secret(key, default=None, required=False):
        """
        Get a secret from environment or raise error.
        
        Priority order:
        1. Environment variable
        2. Secrets file
        3. Default value
        4. Raise error if required
        """
        # Check environment
        if key in os.environ:
            return os.environ[key]
        
        # Check .secrets.json file
        secrets_file = os.path.join(os.path.dirname(__file__), '..', '..', '.secrets.json')
        if os.path.exists(secrets_file):
            try:
                with open(secrets_file, 'r') as f:
                    secrets = json.load(f)
                    if key in secrets:
                        return secrets[key]
            except (json.JSONDecodeError, OSError):
                pass
        
        # Return default or raise
        if required and default is None:
            raise ValueError(f"Required secret '{key}' not found in environment or .secrets.json")
        
        return default
    
    @staticmethod
    def load_all_secrets():
        """Load all secrets from files and environment."""
        secrets = {}
        
        # Load from environment
        env_vars = {
            'DATABASE_URL': 'sqlite:///docpro_database.db',
            'JWT_SECRET_KEY': 'change-me-in-production',
            'CELERY_BROKER_URL': 'redis://localhost:6379/0',
            'CELERY_RESULT_BACKEND': 'redis://localhost:6379/1',
            'API_KEY_SECRET': None,
            'STRIPE_SECRET_KEY': None,
            'STRIPE_PUBLISHABLE_KEY': None,
            'SENDGRID_API_KEY': None,
            'AWS_ACCESS_KEY_ID': None,
            'AWS_SECRET_ACCESS_KEY': None,
            'SENTRY_DSN': None,
        }
        
        for key, default in env_vars.items():
            secrets[key] = os.getenv(key, default)
        
        return secrets

class ProductionConfig:
    """Production environment configuration."""
    
    # Core
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Database - use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = SecretConfig.get_secret(
        'DATABASE_URL',
        'postgresql://user:password@localhost/docpro',
        required=True
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = SecretConfig.get_secret('JWT_SECRET_KEY', required=True)
    JWT_SECRET_KEY = SecretConfig.get_secret('JWT_SECRET_KEY', required=True)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # API
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Celery
    CELERY_BROKER_URL = SecretConfig.get_secret('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = SecretConfig.get_secret('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # File uploads
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
    UPLOAD_FOLDER = '/var/data/docpro/uploads'
    UPLOAD_CHUNKS_DIR = '/var/data/docpro/chunks'
    
    # CORS
    CORS_ALLOW_ORIGIN = os.getenv('CORS_ALLOW_ORIGIN', 'https://yourdomain.com')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/docpro/app.log'
    
    # Stripe (optional)
    STRIPE_SECRET_KEY = SecretConfig.get_secret('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = SecretConfig.get_secret('STRIPE_PUBLISHABLE_KEY')
    
    # Email
    SENDGRID_API_KEY = SecretConfig.get_secret('SENDGRID_API_KEY')
    MAIL_FROM_ADDRESS = 'noreply@yourdomain.com'
    
    # AWS S3 (optional for file storage)
    AWS_ACCESS_KEY_ID = SecretConfig.get_secret('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = SecretConfig.get_secret('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'docpro-files')
    
    # Error tracking
    SENTRY_DSN = SecretConfig.get_secret('SENTRY_DSN')

class DevelopmentConfig:
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Database
    SQLALCHEMY_DATABASE_URI = SecretConfig.get_secret(
        'DATABASE_URL',
        'sqlite:///docpro_database.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # Security
    SECRET_KEY = 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = 'dev-jwt-secret-change-in-production'
    
    # Celery - use local redis or in-memory
    CELERY_BROKER_URL = SecretConfig.get_secret('CELERY_BROKER_URL', 'memory://')
    CELERY_RESULT_BACKEND = SecretConfig.get_secret('CELERY_RESULT_BACKEND', 'cache+memory://')
    
    # File uploads
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    UPLOAD_FOLDER = './uploads'
    UPLOAD_CHUNKS_DIR = './chunks'
    
    # CORS
    CORS_ALLOW_ORIGIN = '*'
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = './logs/app.log'

class TestingConfig:
    """Testing environment configuration."""
    
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    
    # Database - in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    
    # Celery - disable for tests
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    CELERY_ALWAYS_EAGER = True  # Execute tasks synchronously
    
    # File uploads
    UPLOAD_FOLDER = './test_uploads'
    UPLOAD_CHUNKS_DIR = './test_chunks'
    
    # CORS
    CORS_ALLOW_ORIGIN = '*'
    
    # Logging
    LOG_LEVEL = 'WARNING'

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
