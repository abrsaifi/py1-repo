#!/usr/bin/env python3
"""Test script for URL to PDF conversion with formatting"""

import os
import sys
import tempfile

# Import the conversion function from server.py
sys.path.insert(0, 'e:\\OneDrive\\Documents\\py1')
print("[STATUS] Attempting to import url_to_pdf function from server.py...")

try:
    from server import url_to_pdf
    print("[OK] url_to_pdf function imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import url_to_pdf: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test URL to PDF conversion
print("\n--- Testing url_to_pdf with formatting preservation ---")

test_urls = [
    "https://example.com",
    "https://python.org"
]

temp_dir = tempfile.gettempdir()

for test_url in test_urls:
    print(f"\nConverting {test_url}...")
    pdf_output = os.path.join(temp_dir, f"test_url_output_{test_urls.index(test_url)}.pdf")
    
    try:
        result = url_to_pdf(test_url, pdf_output)
        if result:
            print(f"[OK] Conversion succeeded")
            print(f"  Output file: {pdf_output}")
            print(f"  File exists: {os.path.exists(pdf_output)}")
            if os.path.exists(pdf_output):
                file_size = os.path.getsize(pdf_output)
                print(f"  File size: {file_size} bytes")
                if file_size > 500:
                    print(f"[OK] PDF file looks valid (large enough for formatted content)")
                else:
                    print(f"[WARNING] PDF file is small (might be text-only fallback)")
        else:
            print("[ERROR] Conversion returned False")
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}")
        import traceback
        traceback.print_exc()

print("\n--- Test Complete ---")
print("\nNote: Large file sizes indicate formatting was preserved (weasyprint used)")
print("Small file sizes indicate text-only fallback was used")

