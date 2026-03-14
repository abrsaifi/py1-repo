"""Compatibility wrapper for legacy Phase 15 collaboration registration."""
from app.api.routes.phase15_collaboration import bp as collaboration_bp


def register_collaboration_api(app):
    """Register the package-native Phase 15 collaboration blueprint on a Flask app."""
    app.register_blueprint(collaboration_bp)
    return collaboration_bp


def init_collaboration_api(app):
    """Backward-compatible initializer for legacy imports."""
    return register_collaboration_api(app)
