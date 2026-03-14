from app import create_app


def _build_app():
    return create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'tools-catalog-test-secret',
        'JWT_SECRET_KEY': 'tools-catalog-test-jwt-secret-key-0123456789',
        'ENABLE_BACKGROUND_TASKS': False,
        'SCHEMA_BOOTSTRAP_ENABLED': False,
        'ENABLE_WEBSOCKETS': False,
    })


def test_tools_list_uses_shared_catalog():
    app = _build_app()
    client = app.test_client()

    response = client.get('/api/tools')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert len(payload['tools']) >= 60
    assert any(tool['slug'] == 'to-pdf' for tool in payload['tools'])
    assert any(tool['slug'] == 'pdf-to-bw-pro' for tool in payload['tools'])


def test_tool_detail_exposes_parameter_schema():
    app = _build_app()
    client = app.test_client()

    response = client.get('/api/tools/to-pdf')

    assert response.status_code == 200
    payload = response.get_json()
    tool = payload['tool']
    assert tool['slug'] == 'to-pdf'
    assert tool['parameter_key'] == 'To PDF'
    assert tool['settings_label'] == 'Convert to PDF - Advanced Settings'
    assert len(tool['params']) > 10
    assert 'Standard Portrait' in tool['presets']


def test_related_tools_respect_catalog_and_limit():
    app = _build_app()
    client = app.test_client()

    response = client.get('/api/tools/pdf-to-bw/related?limit=2')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert len(payload['related_tools']) == 2
    assert payload['related_tools'][0]['slug'] == 'pdf-to-bw-pro'