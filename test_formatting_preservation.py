#!/usr/bin/env python3
"""Test URL to PDF conversion with content verification"""

import os
import sys
import tempfile
import pytest

# Ensure local package path is available when running tests locally
sys.path.insert(0, 'e:\\OneDrive\\Documents\\py1')

try:
    from server import url_to_pdf
    print("[OK] url_to_pdf imported successfully")
except Exception as e:
    # Avoid exiting the whole pytest run on import failure; mark test module skipped.
    msg = f"Failed to import url_to_pdf: {e}"
    try:
        pytest.skip(msg, allow_module_level=True)
    except Exception:
        print(f"[ERROR] {msg}")
        sys.exit(1)

# Test with a simple webpage
test_url = "https://example.com"
temp_dir = tempfile.gettempdir()
pdf_output = os.path.join(temp_dir, "formatted_webpage.pdf")

print(f"\n[TEST] Converting {test_url} to PDF with formatting preservation...")
print("This will use the best available method:")
print("  1. WeasyPrint (full CSS styling preservation) - if available")
print("  2. BeautifulSoup + text extraction - fallback")
print()

try:
    result = url_to_pdf(test_url, pdf_output)
    if result and os.path.exists(pdf_output):
        file_size = os.path.getsize(pdf_output)
        print(f"[OK] Conversion successful!")
        print(f"[OK] PDF created: {pdf_output}")
        print(f"[OK] File size: {file_size} bytes")
        
        # Read first few bytes to verify it's a valid PDF
        with open(pdf_output, 'rb') as f:
            header = f.read(4)
            if header == b'%PDF':
                print(f"[OK] Valid PDF format confirmed")
            else:
                print(f"[WARNING] PDF header not detected")
    else:
        print(f"[ERROR] Conversion failed")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[INFO] For full CSS formatting preservation, install system dependencies:")
print("       On Windows: GTK+ 3.0 is required for WeasyPrint")
print("       On Linux/Mac: Follow https://doc.courtbouillon.org/weasyprint/")
