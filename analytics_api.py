"""Compatibility wrapper for legacy Phase 15 analytics registration."""
from app.api.routes.phase15_analytics import bp as analytics_bp


def register_analytics_api(app):
    """Register the package-native Phase 15 analytics blueprint on a Flask app."""
    app.register_blueprint(analytics_bp)
    return analytics_bp


def init_analytics_api(app):
    """Backward-compatible initializer for legacy imports."""
    return register_analytics_api(app)
