"""Smoke tests for Phase 15 route registration in the app factory."""

from flask_jwt_extended import create_access_token

from app import create_app
from app.models import User, db


def _build_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'phase15-test-secret',
        'JWT_SECRET_KEY': 'phase15-test-jwt-secret-key-0123456789',
        'ENABLE_BACKGROUND_TASKS': False,
    })

    with app.app_context():
        db.create_all()
        user = User(
            email='phase15@example.com',
            username='phase15-user',
            password_hash='hashed',
            role='user',
        )
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id), additional_claims={
            'role': user.role,
            'username': user.username,
            'email': user.email,
            'is_admin': False,
        })

    return app, {'Authorization': f'Bearer {token}'}


def test_phase15_analytics_routes_are_registered():
    app, headers = _build_app()
    client = app.test_client()

    response = client.get('/api/analytics/dashboard', headers=headers)
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['success'] is True
    assert 'kpis' in payload['data']


def test_phase15_reports_routes_are_registered():
    app, headers = _build_app()
    client = app.test_client()

    create_response = client.post('/api/reports', headers=headers, json={'name': 'Monthly usage'})
    assert create_response.status_code == 201

    response = client.get('/api/reports', headers=headers)
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['success'] is True
    assert isinstance(payload['data'], list)
    assert payload['data'][0]['name'] == 'Monthly usage'


def test_phase15_collaboration_routes_are_registered():
    app, headers = _build_app()
    client = app.test_client()

    document_response = client.post('/api/documents', headers=headers, json={'name': 'Roadmap.pdf', 'file_size': 2048, 'mime_type': 'application/pdf'})
    assert document_response.status_code == 201

    response = client.get('/api/collaboration/dashboard', headers=headers)
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['success'] is True
    assert 'stats' in payload['data']


def test_phase15_notifications_routes_are_registered():
    app, headers = _build_app()
    client = app.test_client()

    report_response = client.post('/api/reports', headers=headers, json={'name': 'Unread notification seed'})
    assert report_response.status_code == 201

    response = client.get('/api/notifications?filter=unread', headers=headers)
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['success'] is True
    assert 'notifications' in payload['data']


def test_phase15_routes_require_authentication():
    app, _ = _build_app()
    client = app.test_client()

    response = client.get('/api/analytics/dashboard')
    assert response.status_code == 401