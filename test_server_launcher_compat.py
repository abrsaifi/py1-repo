from app.main import app as main_app
from server import app as server_app


def test_server_module_exports_modular_app():
    assert server_app is main_app

    client = server_app.test_client()
    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'
