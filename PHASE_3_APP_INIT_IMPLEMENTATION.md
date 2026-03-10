"""Phase 3 Integration Update - Updated app/__init__.py"""

# This is the updated app/__init__.py that integrates all Phase 3 features

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
celery = Celery(__name__)

def create_app(config_name='development'):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'production':
        from app.config_security import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from app.config_security import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from app.config_security import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize database
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        logger.info("✓ SQLAlchemy initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
    
    # Initialize Flask-Limiter
    try:
        limiter.init_app(app)
        logger.info("✓ Flask-Limiter initialized")
    except Exception as e:
        logger.error(f"✗ Rate limiter initialization failed: {str(e)}")
    
    # Initialize caching
    try:
        from app.cache_manager import init_cache
        init_cache(app)
        logger.info("✓ Flask-Caching initialized")
    except Exception as e:
        logger.error(f"✗ Cache initialization failed: {str(e)}")
    
    # Configure database pooling
    try:
        from app.database_pool import configure_database_pooling, cache_warmer
        configure_database_pooling(app, db)
        logger.info("✓ Database pooling configured")
        
        # Warm cache on startup
        with app.app_context():
            cache_warmer(app)
        logger.info("✓ Cache warmed on startup")
    except Exception as e:
        logger.error(f"✗ Database pooling configuration failed: {str(e)}")
    
    # Initialize Celery
    try:
        from app.celery_config import make_celery
        celery_app = make_celery(app)
        logger.info("✓ Celery initialized")
    except Exception as e:
        logger.error(f"✗ Celery initialization failed: {str(e)}")
    
    # Register security middleware
    try:
        from app.middleware.security import security_headers
        security_headers(app)
        logger.info("✓ Security headers configured")
    except Exception as e:
        logger.error(f"✗ Security middleware initialization failed: {str(e)}")
    
    # Register blueprints
    try:
        from app.api.routes.admin import admin_bp
        app.register_blueprint(admin_bp)
        logger.info("✓ Admin API routes registered")
    except Exception as e:
        logger.error(f"✗ Admin API registration failed: {str(e)}")
    
    # Register analytics routes (Phase 3)
    try:
        from app.api.routes.analytics import analytics_bp
        app.register_blueprint(analytics_bp)
        logger.info("✓ Analytics API routes registered")
    except Exception as e:
        logger.warning(f"⚠ Analytics API registration incomplete: {str(e)}")
    
    # Register webhook routes (Phase 3)
    try:
        from app.api.routes.webhooks import webhooks_bp
        app.register_blueprint(webhooks_bp)
        logger.info("✓ Webhook API routes registered")
    except Exception as e:
        logger.warning(f"⚠ Webhook API registration incomplete: {str(e)}")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }, 200
    
    return app

def make_celery(app):
    """Configure Celery with Flask app."""
    from app.celery_config import celery as celery_app
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    celery_app.conf.update(app.config)
    
    return celery_app

# IMPLEMENTATION NOTES:
# 
# 1. This file integrates all Phase 3 features with Phase 1-2 foundation
# 2. New imports required:
#    - cache_manager: Redis caching layer
#    - database_pool: Connection pooling
#    - analytics routes: Advanced analytics API
#    - webhook routes: Webhook management API
# 
# 3. Initialization order matters:
#    - Database first (required by all models)
#    - Cache second (used by analytics)
#    - Limiter third (protects endpoints)
#    - Celery fourth (runs tasks)
#    - Security last (wraps everything)
# 
# 4. Environment variables required (set in .env):
#    - REDIS_URL: Redis connection (default: redis://localhost:6379/0)
#    - CACHE_TYPE: Flask-Cache backend (default: redis)
#    - CACHE_REDIS_URL: Cache connection
#    - SQLALCHEMY_POOL_SIZE: Connection pool size
#    - SQLALCHEMY_MAX_OVERFLOW: Max pool overflow
# 
# 5. All error handling uses try/except to ensure partial
#    failures don't prevent app startup
# 
# 6. Replace this entire __init__.py file with this version
