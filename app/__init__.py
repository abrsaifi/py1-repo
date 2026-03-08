from flask import Flask
from .config import Config
from .utils.errors import register_error_handlers
from .utils.logger_setup import LoggerSetup
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

    # Enable CORS for API endpoints in the package app so the frontend can
    # fetch `/api/*` during development. Prefer `flask_cors` if available.
    try:
        from flask_cors import CORS
        CORS(app, resources={r"/api/*": {"origins": "*"}})
        app.logger.info('flask_cors enabled for /api/* in package app')
    except Exception:
        @app.after_request
        def _add_cors_headers(response):
            try:
                path = getattr(request, 'path', '')
                if path.startswith('/api/'):
                    response.headers['Access-Control-Allow-Origin'] = os.environ.get('CORS_ALLOW_ORIGIN', '*')
                    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
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
    
    # INTEGRATION: Register error handlers
    register_error_handlers(app)
    app.logger.info('Error handlers registered')
    
    # INTEGRATION: Initialize background tasks
    try:
        from .startup import init_background_tasks
        init_background_tasks()
        app.logger.info('Background tasks initialized')
    except Exception as e:
        app.logger.warning(f'Background tasks initialization failed (non-critical): {str(e)}')

    return app
