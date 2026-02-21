import io
import base64
from server import app


def _make_pdf_bytes():
    # create a minimal PDF using reportlab
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 700, "Preview Test PDF")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def test_preview_pdf(client=None):
    if client is None:
        app.config['TESTING'] = True
        client = app.test_client()

    pdf_bytes = _make_pdf_bytes()
    data = {'files': (pdf_bytes, 'test.pdf'), 'operation': 'bw'}
    resp = client.post('/preview', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    j = resp.get_json()
    assert j['success'] is True
    assert j['image'].startswith('data:image/png;base64,')
