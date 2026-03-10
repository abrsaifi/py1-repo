"""
Analytics Service Configuration
"""

import os
from datetime import timedelta


class BaseConfig:
    """Base configuration for all environments"""
    
    # Service info
    SERVICE_NAME = 'analytics-service'
    SERVICE_VERSION = '1.0.0'
    SERVICE_PORT = 5009
    
    # Flask
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'ANALYTICS_DATABASE_URL',
        'postgresql://analytics_user:analytics_pass@localhost:5432/analytics_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_ECHO = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_CACHE_TTL = 300  # 5 minutes default
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-me-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Analytics Configuration
    # Time-series aggregation
    METRIC_AGGREGATION_INTERVALS = {
        'minute': 60,        # 60 seconds
        'hour': 3600,       # 1 hour
        'day': 86400,       # 1 day
        'week': 604800,     # 1 week
        'month': 2592000,   # approx 30 days
        'year': 31536000    # 365 days
    }
    
    # Default aggregation granularity when not specified
    DEFAULT_AGGREGATION_LEVEL = 'hour'
    
    # Data retention policies (in days)
    RETENTION_POLICIES = {
        'minute': 7,        # Keep minute-level data for 7 days
        'hour': 30,         # Keep hour-level data for 30 days
        'day': 365,         # Keep daily data for 1 year
        'week': 1095,       # Keep weekly data for 3 years
        'month': 2555,      # Keep monthly data for 7 years
        'year': 10000       # Keep yearly data indefinitely
    }
    
    # Query limits
    MAX_QUERY_RESULTS = 10000
    MAX_QUERY_TIME_RANGE_DAYS = 730  # 2 years max
    DEFAULT_QUERY_LIMIT = 100
    
    # Dashboard settings
    DEFAULT_DASHBOARD_AUTO_REFRESH = 300  # 5 minutes in seconds
    MAX_DASHBOARD_WIDGETS = 50
    DASHBOARD_CACHE_TTL = 60  # 1 minute
    
    # Report settings
    REPORT_OUTPUT_DIR = os.getenv('REPORT_OUTPUT_DIR', '/tmp/reports')
    REPORT_RETENTION_DAYS = 90  # Keep reports for 90 days
    SUPPORTED_REPORT_FORMATS = ['pdf', 'xlsx', 'html', 'csv']
    DEFAULT_REPORT_FORMAT = 'pdf'
    
    # Alert settings
    ALERT_EVALUATION_FREQUENCY = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '1h': 3600
    }
    DEFAULT_ALERT_FREQUENCY = '5m'
    ALERT_RETENTION_DAYS = 180  # Keep alert events for 180 days
    
    # Anomaly detection
    ANOMALY_DETECTION_ENABLED = True
    ANOMALY_WINDOW_SIZE = 30  # Use last 30 data points for baseline
    ANOMALY_SENSITIVITY_LEVELS = {
        'low': 0.2,      # 20% deviation
        'medium': 0.15,  # 15% deviation
        'high': 0.1      # 10% deviation
    }
    DEFAULT_ANOMALY_SENSITIVITY = 0.15
    
    # Notification channels
    NOTIFICATION_CHANNELS = ['email', 'slack', 'webhook', 'sms']
    
    # Cache
    CACHE_DEFAULT_TTL = 300  # 5 minutes
    CACHE_METRIC_TTL = 300   # 5 minutes for metric queries
    CACHE_DASHBOARD_TTL = 60  # 1 minute for dashboard data
    CACHE_REPORT_TTL = 3600   # 1 hour for report templates
    
    # Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 500
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = '100/hour'
    RATELIMIT_BY_IP = True
    
    # Metrics processor settings
    METRICS_PROCESSOR_BATCH_SIZE = 1000
    METRICS_PROCESSOR_FLUSH_INTERVAL = 60  # seconds
    PERCENTILE_CALCULATION_METHOD = 'linear'  # 'linear' or 'nearest'
    
    # Business metrics
    FINANCIAL_PRECISION = 2  # Decimal places for currency
    LTV_CALCULATION_PERIOD_MONTHS = 12
    CHURN_DEFINITION_DAYS = 30  # User inactive for 30 days = churned
    
    # Feature usage tracking
    TRACK_FEATURE_USAGE = True
    FEATURE_USAGE_SAMPLE_RATE = 0.1  # Sample 10% of events
    
    # Device/Browser tracking
    TRACK_DEVICE_METRICS = True
    TRACK_GEO_METRICS = True
    
    # Custom metric
    CUSTOM_METRIC_MAX_FORMULA_LENGTH = 500
    CUSTOM_METRIC_TIMEOUT_SECONDS = 30
    SUPPORTED_METRIC_AGGREGATIONS = ['count', 'sum', 'avg', 'min', 'max', 'rate', 'percentage']


class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'
    CACHE_DEFAULT_TTL = 60  # Shorter cache for dev
    RATELIMIT_ENABLED = False


class TestingConfig(BaseConfig):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    REDIS_URL = 'redis://localhost:6379/1'  # Use different Redis DB
    CACHE_DEFAULT_TTL = 0  # No caching in tests
    RATELIMIT_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    MAX_QUERY_RESULTS = 100  # Smaller limit for tests


class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'WARNING'
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Stricter rate limiting
    RATELIMIT_DEFAULT = '50/hour'
    
    # Shorter cache for freshness
    CACHE_DEFAULT_TTL = 60
    
    # Larger pools for production
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_MAX_OVERFLOW = 40


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
}


def get_config(config_name='development'):
    """Get configuration object by name"""
    return config_by_name.get(config_name, DevelopmentConfig)
