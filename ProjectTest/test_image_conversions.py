import os
import os
import io
import zipfile
from PIL import Image
import tempfile
import pytest
from server import app, convert_image_format


def make_test_image(path, fmt='PNG'):
    img = Image.new('RGBA', (100, 60), (255, 0, 0, 255))
    img.save(path, fmt)
    img.close()


def test_convert_image_format_direct(tmp_path):
    inp = tmp_path / 'in.png'
    out = tmp_path / 'out.jpg'
    make_test_image(str(inp), fmt='PNG')

    ok = convert_image_format(str(inp), str(out), 'jpg', quality=80)
    assert ok
    assert out.exists()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_convert_image_route_single(client, tmp_path):
    inp = tmp_path / 'in.png'
    make_test_image(str(inp), fmt='PNG')

    data = {
        'target_format': 'jpg',
        'quality': '75'
    }
    with open(inp, 'rb') as f:
        data['file'] = (f, 'in.png')
        resp = client.post('/convert-image', data=data, content_type='multipart/form-data')

    assert resp.status_code == 200
    # Should be a JPEG file stream
    content_disp = resp.headers.get('Content-Disposition', '')
    assert 'attachment' in content_disp


def test_convert_image_route_multiple(client, tmp_path):
    inp1 = tmp_path / 'a.png'
    inp2 = tmp_path / 'b.png'
    make_test_image(str(inp1), fmt='PNG')
    make_test_image(str(inp2), fmt='PNG')

    # Use werkzeug to send multiple files
    with open(inp1, 'rb') as f1, open(inp2, 'rb') as f2:
        resp = client.post('/convert-image', data={
            'target_format': 'webp',
            'quality': '85',
            'lossless': 'true',
            'file': [ (f1, 'a.png'), (f2, 'b.png') ]
        }, content_type='multipart/form-data')

    assert resp.status_code == 200
    content_disp = resp.headers.get('Content-Disposition', '')
    assert 'attachment' in content_disp
    # Expect a zip when multiple
    assert 'zip' in resp.headers.get('Content-Type', '') or resp.data[:2] == b'PK'