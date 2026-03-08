import requests
from PIL import Image
import io

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Test /convert-to-pdf with 'files' field (as sent by the template)
print("Testing /convert-to-pdf with 'files' field (from template)...")
files = {
    'files': ('test.png', img_bytes, 'image/png')
}
resp = requests.post('http://localhost:5000/convert-to-pdf', files=files, timeout=10)
print(f"Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type', 'N/A')}")
if resp.status_code == 200:
    print("✓ SUCCESS: /convert-to-pdf accepts 'files' field")
else:
    print(f"✗ FAILED: got {resp.status_code}, body: {resp.text[:200]}")
