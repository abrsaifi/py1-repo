from app import create_app


def _build_app():
    return create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'api-docs-test-secret',
        'JWT_SECRET_KEY': 'api-docs-test-jwt-secret-key-0123456789',
        'ENABLE_BACKGROUND_TASKS': False,
        'SCHEMA_BOOTSTRAP_ENABLED': False,
        'ENABLE_WEBSOCKETS': False,
    })


def test_openapi_endpoint_exposes_active_routes():
    app = _build_app()
    client = app.test_client()

    response = client.get('/api/openapi.json')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['openapi'] == '3.0.3'
    assert '/api/auth/login' in payload['paths']
    assert '/api/analytics/dashboard' in payload['paths']
    assert '/api/upload-chunk' in payload['paths']
    assert '/api/admin/users' in payload['paths']
    assert payload['paths']['/api/auth/login']['post']['security'] == []
    assert payload['paths']['/api/analytics/dashboard']['get']['security'] == [{'BearerAuth': []}]
    assert payload['paths']['/api/upload-chunk']['post']['security'] == [{'ApiKeyAuth': []}]
    assert payload['components']['schemas']['AuthLoginRequest']['required'] == ['username', 'password']
    assert payload['paths']['/api/auth/login']['post']['requestBody']['content']['application/json']['schema']['$ref'] == '#/components/schemas/AuthLoginRequest'
    assert payload['paths']['/api/upload-status']['get']['parameters'][0]['name'] == 'upload_id'
    assert 'application/zip' in payload['paths']['/api/convert-uploaded']['post']['responses']['200']['content']
    assert any(tag['name'] == 'auth' for tag in payload['tags'])


def test_swagger_ui_route_is_available():
    app = _build_app()
    client = app.test_client()

    response = client.get('/api/docs/')

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert 'SwaggerUIBundle' in page
    assert '/api/openapi.json' in page