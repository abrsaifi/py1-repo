from flask import Flask, request
from .config import Config
from .utils.errors import register_error_handlers
from .utils.logger_setup import LoggerSetup
from .models import db
import os
import tempfile


def create_app(config=None):
    """Factory to create a Flask app for the refactored package layout.

    This is intentionally lightweight so it can be used while we incrementally
    migrate functionality out of the legacy `server.py`.
    """
    app = Flask(__name__, instance_relative_config=False)
    # load defaults from Config
    try:
        app.config.from_object(Config)
    except Exception:
        pass
    # allow overriding from passed config dict
    if config:
        app.config.update(config)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Migrate for database migrations
    try:
        from flask_migrate import Migrate
        Migrate(app, db)
    except ImportError:
        pass  # Flask-Migrate not installed yet
    
    # INTEGRATION: Setup logging
    log_file = app.config.get('LOG_FILE', os.path.join(os.path.dirname(__file__), '..', 'logs', 'app.log'))
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', 'standard')
    use_json = log_format == 'json'
    
    logger = LoggerSetup.setup(
        app_name='docpro',
        level=log_level,
        log_file=log_file,
        use_json=use_json
    )
    app.logger = logger
    logger.info('Application initialized with structured logging')
    
    # INTEGRATION: Initialize Celery for background tasks
    try:
        from .celery_config import make_celery
        celery = make_celery(app)
        app.celery = celery
        app.logger.info('Celery initialized for background task processing')
    except ImportError:
        app.logger.warning('Celery not installed - background tasks disabled')
    except Exception as e:
        app.logger.warning(f'Celery initialization failed: {str(e)}')
    
    # INTEGRATION: Add security headers and middleware
    try:
        from .middleware.security import security_headers
        security_headers(app)
        app.logger.info('Security headers middleware enabled')
    except Exception as e:
        app.logger.warning(f'Security headers setup failed: {str(e)}')
    
    # INTEGRATION: Register health check blueprint (Task 6 - Load Balancing & HA)
    try:
        from .health_check import health_bp
        app.register_blueprint(health_bp)
        app.logger.info('Health check endpoints registered for load balancer')
    except Exception as e:
        app.logger.warning(f'Health check registration failed: {str(e)}')
    
    # INTEGRATION: Initialize auto-scaling manager (Task 7 - Auto-Scaling)
    try:
        from .autoscaling_manager import (
            get_autoscaling_manager,
            get_metrics_collector,
            ScalingPolicies
        )
        manager = get_autoscaling_manager()
        collector = get_metrics_collector()
        app.config['AUTOSCALING_MANAGER'] = manager
        app.config['METRICS_COLLECTOR'] = collector
        app.logger.info(f'Auto-scaling manager initialized with {manager.policy.name} policy')
    except ImportError:
        app.logger.warning('Auto-scaling manager not available (optional dependency)')
    except Exception as e:
        app.logger.warning(f'Auto-scaling manager initialization failed: {str(e)}')

    # Enable CORS for API endpoints and health endpoints in the package app so the frontend can
    # fetch `/api/*` during development. Prefer `flask_cors` if available.
    try:
        from flask_cors import CORS
        CORS(app, 
             resources={
                 r"/api/*": {"origins": "*"},
                 r"/health*": {"origins": "*"}
             },
             supports_credentials=True)
        app.logger.info('flask_cors enabled for /api/* and /health* in package app')
    except Exception:
        @app.after_request
        def _add_cors_headers(response):
            try:
                path = getattr(request, 'path', '')
                if path.startswith('/api/') or path.startswith('/health'):
                    response.headers['Access-Control-Allow-Origin'] = os.environ.get('CORS_ALLOW_ORIGIN', '*')
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
            except Exception:
                pass
            return response

    # ensure upload directory exists
    try:
        os.makedirs(app.config.get('UPLOAD_CHUNKS_DIR', os.path.join(tempfile.gettempdir(), 'docpro_uploads')), exist_ok=True)
    except Exception:
        pass

    # Register available blueprints (health is always present)
    try:
        from .api.routes.health import bp as health_bp
        app.register_blueprint(health_bp, url_prefix='/api')
    except Exception:
        pass
    # register other blueprints if present
    try:
        from .api.routes.image import bp as image_bp
        app.register_blueprint(image_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.pdf import bp as pdf_bp
        app.register_blueprint(pdf_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.excel import bp as excel_bp
        app.register_blueprint(excel_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.uploads import bp as uploads_bp
        app.register_blueprint(uploads_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.data import bp as data_bp
        app.register_blueprint(data_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.analytics import bp as analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.tools import bp as tools_bp
        app.register_blueprint(tools_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')
    except Exception:
        pass
    # Register scaling routes (Task 7)
    try:
        from .api.routes.scaling import bp as scaling_bp
        app.register_blueprint(scaling_bp)
        app.logger.info('Scaling API routes registered at /api/scaling')
    except Exception as e:
        app.logger.warning(f'Scaling routes registration failed (optional): {str(e)}')
    # Register compliance routes (Task 8)
    try:
        from .api.routes.compliance import bp as compliance_bp
        app.register_blueprint(compliance_bp)
        app.logger.info('Compliance API routes registered at /api/compliance')
    except Exception as e:
        app.logger.warning(f'Compliance routes registration failed (optional): {str(e)}')
    
    # Register disaster recovery routes (Task 9)
    try:
        from .api.routes.disaster_recovery import bp as disaster_recovery_bp
        app.register_blueprint(disaster_recovery_bp)
        app.logger.info('Disaster recovery API routes registered at /api/disaster-recovery')
    except Exception as e:
        app.logger.warning(f'Disaster recovery routes registration failed (optional): {str(e)}')
    
    # Register multi-region routes (Task 10)
    try:
        from .api.routes.multi_region import bp as multi_region_bp
        app.register_blueprint(multi_region_bp)
        app.logger.info('Multi-region API routes registered at /api/multi-region')
    except Exception as e:
        app.logger.warning(f'Multi-region routes registration failed (optional): {str(e)}')
    
    # Register admin routes
    try:
        from .api.routes.admin import bp as admin_bp
        app.register_blueprint(admin_bp)
        app.logger.info('Admin routes registered at /api/admin')
    except Exception as e:
        app.logger.warning(f'Admin routes registration failed: {str(e)}')
    # sitemap & robots (served at root)
    try:
        from .api.routes.seo import bp as seo_bp
        app.register_blueprint(seo_bp)
    except Exception:
        pass
    
    # INTEGRATION: Initialize background tasks (before error handlers)
    try:
        from .startup import init_background_tasks
        init_background_tasks()
        app.logger.info('Background tasks initialized')
    except Exception as e:
        app.logger.warning(f'Background tasks initialization failed (non-critical): {str(e)}')

    # INTEGRATION: Register error handlers
    register_error_handlers(app)
    app.logger.info('Error handlers registered')

    return app
