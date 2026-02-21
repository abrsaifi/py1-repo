from flask import Flask
from .config import Config
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
        from .api.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.advanced import bp as advanced_bp
        app.register_blueprint(advanced_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.webhooks_api import bp as webhooks_bp
        app.register_blueprint(webhooks_bp, url_prefix='/api')
    except Exception:
        pass
    try:
        from .api.routes.dashboard import bp as dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/api')
    except Exception:
        pass

    return app
