#!/usr/bin/env python3
"""Test script for HTML conversion functions"""

import os
import sys
import tempfile

# Import the conversion functions from server.py
sys.path.insert(0, 'e:\\OneDrive\\Documents\\py1')
print("[STATUS] Attempting to import conversion functions from server.py...")

try:
    from server import html_to_pdf, pdf_to_html
    print("[OK] Conversion functions imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import conversion functions: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 1: HTML to PDF
print("\n--- Testing html_to_pdf ---")
test_html = """<h1>Test Document</h1>
<p>This is a test paragraph with some content.</p>
<p>Here is another paragraph to test the conversion.</p>"""

temp_dir = tempfile.gettempdir()
pdf_output = os.path.join(temp_dir, "test_html_output.pdf")

try:
    result = html_to_pdf(test_html, pdf_output)
    if result:
        print(f"[OK] HTML to PDF conversion succeeded")
        print(f"  Output file: {pdf_output}")
        print(f"  File exists: {os.path.exists(pdf_output)}")
        print(f"  File size: {os.path.getsize(pdf_output)} bytes")
    else:
        print("[ERROR] HTML to PDF conversion returned False")
except Exception as e:
    print(f"[ERROR] HTML to PDF conversion failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: PDF to HTML
print("\n--- Testing pdf_to_html ---")
if os.path.exists(pdf_output):
    html_output = os.path.join(temp_dir, "test_pdf_output.html")
    try:
        result = pdf_to_html(pdf_output, html_output)
        if result:
            print(f"[OK] PDF to HTML conversion succeeded")
            print(f"  Output file: {html_output}")
            print(f"  File exists: {os.path.exists(html_output)}")
            print(f"  File size: {os.path.getsize(html_output)} bytes")
            
            # Read and display content preview
            with open(html_output, 'r', encoding='utf-8') as f:
                content = f.read()
                preview_length = min(200, len(content))
                print(f"  Content preview: {content[:preview_length]}...")
        else:
            print("[ERROR] PDF to HTML conversion returned False")
    except Exception as e:
        print(f"[ERROR] PDF to HTML conversion failed: {e}")
        import traceback
        traceback.print_exc()

print("\n--- Test Complete ---")
