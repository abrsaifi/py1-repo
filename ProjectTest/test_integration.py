import requests
from PIL import Image
import io
from pathlib import Path
import tempfile
import fitz

print("=== COMPREHENSIVE INTEGRATION TEST ===\n")

# 1. Test Convert to PDF with image (template sends 'files' field)
print("1. Testing /convert-to-pdf with image (template format)...")
img = Image.new('RGB', (50, 50), color='blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

files = {'files': ('image.png', img_bytes, 'image/png')}
resp = requests.post('http://localhost:5000/convert-to-pdf', files=files, timeout=10)
print(f"   Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
assert 'pdf' in resp.headers.get('content-type', '').lower(), "Expected PDF response"
print("   ✓ PASS\n")

# 2. Test PDF to B&W conversion with 'files' field
print("2. Testing /convert (PDF to B&W) with 'files' field...")
temp_dir = tempfile.mkdtemp()
pdf_path = Path(temp_dir) / "test.pdf"
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Color PDF")
doc.save(str(pdf_path))
doc.close()

with open(pdf_path, 'rb') as f:
    files = {'files': ('test.pdf', f, 'application/pdf')}
    resp = requests.post('http://localhost:5000/convert', files=files, data={
        'dpi': '300',
        'threshold': '250',
        'contrast': '3.0', 
        'sharpness': '2.5'
    }, timeout=15)
    print(f"   Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert 'pdf' in resp.headers.get('content-type', '').lower(), "Expected PDF response"
    print("   ✓ PASS\n")

# 3. Test PDF extraction with 'files' field
print("3. Testing /pdf-extract with 'files' field...")
with open(pdf_path, 'rb') as f:
    files = {'files': ('test.pdf', f, 'application/pdf')}
    resp = requests.post('http://localhost:5000/pdf-extract', files=files, data={
        'format': 'docx'
    }, timeout=15)
    print(f"   Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert 'word' in resp.headers.get('content-type', '').lower() or 'document' in resp.headers.get('content-type', '').lower(), "Expected DOCX response"
    print("   ✓ PASS\n")

# 4. Test OCR with 'files' field
print("4. Testing /ocr with 'files' field...")
img = Image.new('RGB', (100, 100), color='white')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

files = {'files': ('image.png', img_bytes, 'image/png')}
resp = requests.post('http://localhost:5000/ocr', files=files, timeout=20)
print(f"   Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
print("   ✓ PASS\n")

import shutil
shutil.rmtree(temp_dir)

print("=" * 40)
print("ALL INTEGRATION TESTS PASSED ✓")
print("=" * 40)
