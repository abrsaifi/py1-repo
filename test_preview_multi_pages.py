import io
from server import app


def _make_multi_page_pdf():
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for i in range(1,6):
        c.drawString(100, 700, f"Page {i}")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf


def test_preview_multi_pages():
    app.config['TESTING'] = True
    client = app.test_client()
    pdf = _make_multi_page_pdf()
    data = {'files': (pdf, 'multipage.pdf'), 'operation': 'bw', 'max_pages': '4'}
    resp = client.post('/preview', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    j = resp.get_json()
    assert j['success'] is True
    assert 'images' in j and len(j['images']) == 4
