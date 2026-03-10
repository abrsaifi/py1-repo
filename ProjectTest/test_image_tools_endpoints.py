import io
import os
import pytest
from server import app

TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'test_sample.jpg')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def make_image_file():
    # create a tiny red JPEG in-memory if sample file not present
    try:
        from PIL import Image
        buf = io.BytesIO()
        img = Image.new('RGB', (32, 32), color=(255, 0, 0))
        img.save(buf, format='JPEG')
        buf.seek(0)
        return buf
    except Exception:
        # fallback to empty bytes
        return io.BytesIO(b'\xff\xd8\xff')


def test_compress_image(client):
    data = {
        'quality': '70'
    }
    img = make_image_file()
    data['file'] = (img, 'sample.jpg')

    resp = client.post('/compress-image', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    assert resp.data[:2] == b'\xff\xd8' or resp.headers.get('Content-Type') in ('image/jpeg', 'image/jpg')


def test_resize_image(client):
    data = {'width': '64', 'height': '64'}
    img = make_image_file()
    data['file'] = (img, 'sample.jpg')

    resp = client.post('/resize-image', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    assert resp.data[:2] == b'\xff\xd8' or resp.headers.get('Content-Type') in ('image/jpeg',)


def test_bg_to_white(client):
    img = make_image_file()
    data = {'file': (img, 'sample.png')}
    resp = client.post('/bg-to-white', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200


def test_watermark(client):
    img = make_image_file()
    data = {'file': (img, 'sample.png'), 'watermark_text': 'TEST', 'opacity': '0.5'}
    resp = client.post('/watermark', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200


def test_compress_pdf_requires_pdf(client):
    # Sending an image to /compress-pdf should return 400
    img = make_image_file()
    data = {'file': (img, 'sample.jpg')}
    resp = client.post('/compress-pdf', data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
