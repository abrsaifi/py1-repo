"""Test Flask app factory and basic setup."""
import pytest
from app import create_app


def test_app_creation():
    """Test that app factory creates Flask app."""
    app = create_app()
    assert app is not None
    assert app.name == 'app'


def test_app_config():
    """Test that app loads config correctly."""
    app = create_app()
    assert app.config['SECRET_KEY']
    assert app.config['MAX_CONTENT_LENGTH'] > 0


def test_health_endpoint():
    """Test health check endpoint."""
    app = create_app()
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'
