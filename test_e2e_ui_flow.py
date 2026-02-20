import io
import pytest
from server import app
from reportlab.pdfgen import canvas

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def make_image_bytes():
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new('RGB', (100, 100), color=(10, 120, 200))
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def make_pdf_bytes():
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "Test PDF")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def test_index_and_ui_flow(client):
    # GET index
    resp = client.get('/')
    assert resp.status_code == 200

    # Image compress flow
    img = make_image_bytes()
    data = {'quality': '70', 'file': (img, 'test.png')}
    resp = client.post('/compress-image', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200

    # PDF compress flow
    pdf = make_pdf_bytes()
    data = {'optimize_for': 'web', 'remove_metadata': 'true', 'image_quality': '75', 'file': (pdf, 'doc.pdf')}
    resp = client.post('/compress-pdf', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200

    # Resize flow
    img2 = make_image_bytes()
    data = {'width': '64', 'height': '64', 'file': (img2, 'test2.png')}
    resp = client.post('/resize-image', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200

    # BG to white
    img3 = make_image_bytes()
    data = {'method': 'alpha', 'file': (img3, 'test3.png')}
    resp = client.post('/bg-to-white', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200

    # Watermark via UI
    img4 = make_image_bytes()
    data = {'watermark_text': 'UI TEST', 'opacity': '0.4', 'file': (img4, 'test4.png')}
    resp = client.post('/watermark', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
