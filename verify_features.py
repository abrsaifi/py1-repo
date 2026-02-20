import io
import sys
from PIL import Image
from reportlab.pdfgen import canvas
from server import app

app.config['TESTING'] = True
client = app.test_client()

print("=" * 60)
print("FEATURE VERIFICATION REPORT")
print("=" * 60)

features = []

# Test 1: Image Compression
try:
    img_buf = io.BytesIO()
    img = Image.new('RGB', (200, 200), color=(100, 150, 200))
    img.save(img_buf, format='PNG')
    img_buf.seek(0)
    resp = client.post('/compress-image', data={'quality': '70', 'file': (img_buf, 'test.png')}, content_type='multipart/form-data')
    features.append(("🗜️ Image Compression", resp.status_code == 200))
except Exception as e:
    features.append(("🗜️ Image Compression", False))

# Test 2: PDF Compression
try:
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf)
    c.drawString(100, 750, "Test PDF")
    c.showPage()
    c.save()
    pdf_buf.seek(0)
    resp = client.post('/compress-pdf', data={'optimize_for': 'web', 'remove_metadata': 'true', 'image_quality': '75', 'file': (pdf_buf, 'doc.pdf')}, content_type='multipart/form-data')
    features.append(("📦 PDF Compression", resp.status_code == 200))
except Exception as e:
    features.append(("📦 PDF Compression", False))

# Test 3: Image Resize
try:
    img_buf = io.BytesIO()
    img = Image.new('RGB', (600, 400), color=(50, 100, 150))
    img.save(img_buf, format='PNG')
    img_buf.seek(0)
    resp = client.post('/resize-image', data={'width': '300', 'height': '200', 'file': (img_buf, 'test.png')}, content_type='multipart/form-data')
    features.append(("📐 Image Resize", resp.status_code == 200))
except Exception as e:
    features.append(("📐 Image Resize", False))

# Test 4: Background to White
try:
    img_buf = io.BytesIO()
    img = Image.new('RGBA', (150, 150), color=(200, 100, 50, 255))
    img.save(img_buf, format='PNG')
    img_buf.seek(0)
    resp = client.post('/bg-to-white', data={'method': 'alpha', 'file': (img_buf, 'test.png')}, content_type='multipart/form-data')
    features.append(("⚪ BG → White", resp.status_code == 200))
except Exception as e:
    features.append(("⚪ BG → White", False))

# Test 5: Image Watermark
try:
    img_buf = io.BytesIO()
    img = Image.new('RGB', (400, 300), color=(200, 200, 200))
    img.save(img_buf, format='PNG')
    img_buf.seek(0)
    resp = client.post('/watermark', data={'watermark_text': 'TEST', 'position': 'center', 'opacity': '0.5', 'file': (img_buf, 'test.png')}, content_type='multipart/form-data')
    features.append(("💧 Watermark (Image)", resp.status_code == 200))
except Exception as e:
    features.append(("💧 Watermark (Image)", False))

# Print results
for feature, status in features:
    symbol = "✅" if status else "❌"
    print(f"{symbol} {feature:30s} {'PASS' if status else 'FAIL'}")

# Summary
passed = sum(1 for _, status in features if status)
total = len(features)
print("=" * 60)
print(f"Result: {passed}/{total} features working")
print("=" * 60)

sys.exit(0 if passed == total else 1)
