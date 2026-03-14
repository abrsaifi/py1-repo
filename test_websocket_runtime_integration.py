from app import create_app
from websocket_events import get_websocket_manager


def _build_app():
    return create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'websocket-test-secret',
        'JWT_SECRET_KEY': 'websocket-test-jwt-secret-key-0123456789',
        'ENABLE_BACKGROUND_TASKS': False,
        'SCHEMA_BOOTSTRAP_ENABLED': False,
        'ENABLE_WEBSOCKETS': True,
    })


def test_app_factory_initializes_websocket_server():
    app = _build_app()
    socketio = app.extensions.get('socketio')

    assert socketio is not None

    flask_client = app.test_client()
    client = socketio.test_client(app, flask_test_client=flask_client)

    assert client.is_connected()

    received = client.get_received()
    assert any(
        event['name'] == 'connection_response'
        and event['args']
        and event['args'][0]['status'] == 'connected'
        for event in received
    )

    client.disconnect()


def test_job_update_handlers_attach_to_active_socketio_server():
    app = _build_app()
    socketio = app.extensions.get('socketio')
    manager = app.extensions.get('job_websocket_manager')

    assert socketio is not None
    assert manager is get_websocket_manager()

    flask_client = app.test_client()
    client = socketio.test_client(app, flask_test_client=flask_client)

    ack = client.emit('watch_job', {'job_id': 'job-123'}, callback=True)
    assert ack == {'success': True, 'message': 'Watching job job-123'}

    manager.notify_job_progress('job-123', 55, 'Halfway there')

    received = client.get_received()
    assert any(
        event['name'] == 'job_update'
        and event['args']
        and event['args'][0]['job_id'] == 'job-123'
        and event['args'][0]['data']['event'] == 'progress'
        and event['args'][0]['data']['progress'] == 55
        for event in received
    )

    client.disconnect()