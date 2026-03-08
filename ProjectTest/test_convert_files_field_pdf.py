import requests
import tempfile
from pathlib import Path
import fitz

# Create a simple test PDF
temp_dir = tempfile.mkdtemp()
test_pdf_path = Path(temp_dir) / "test.pdf"
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "Test PDF")
doc.save(str(test_pdf_path))
doc.close()

# Test /convert with 'files' field (template format)
print("Testing /convert with 'files' field (template format)...")
with open(test_pdf_path, 'rb') as f:
    files = {
        'files': ('test.pdf', f, 'application/pdf')
    }
    resp = requests.post('http://localhost:5000/convert', files=files, data={
        'dpi': '300',
        'threshold': '250',
        'contrast': '3.0',
        'sharpness': '2.5'
    }, timeout=15)
    print(f"Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type', 'N/A')}")
    if resp.status_code == 200:
        print("✓ SUCCESS: /convert accepts 'files' field")
    else:
        print(f"✗ FAILED: got {resp.status_code}, body: {resp.text[:200]}")

import shutil
shutil.rmtree(temp_dir)
