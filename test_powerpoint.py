#!/usr/bin/env python3
"""Test script for PowerPoint conversion functions"""

import os
import sys
import tempfile

# Test imports
try:
    from pptx import Presentation
    print("[OK] python-pptx installed successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import python-pptx: {e}")
    sys.exit(1)

try:
    import fitz  # PyMuPDF
    print("[OK] PyMuPDF installed successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import PyMuPDF: {e}")
    sys.exit(1)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    print("[OK] reportlab installed successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import reportlab: {e}")
    sys.exit(1)

# Import the conversion functions from server.py
sys.path.insert(0, 'e:\\OneDrive\\Documents\\py1')
print("[STATUS] Attempting to import conversion functions from server.py...")
print("[STATUS] Reading server.py...")
try:
    from server import pdf_to_powerpoint, powerpoint_to_pdf
    print("[OK] Conversion functions imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import conversion functions: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create a simple test PDF
print("\n--- Creating test PDF ---")
test_pdf_path = os.path.join(tempfile.gettempdir(), "test_input.pdf")
doc = fitz.open()  # Create blank PDF
page = doc.new_page()
text = "Test PDF Page 1"
page.insert_text((50, 50), text, fontsize=20)
doc.save(test_pdf_path)
doc.close()
print(f"[OK] Created test PDF: {test_pdf_path}")

# Test pdf_to_powerpoint
print("\n--- Testing pdf_to_powerpoint ---")
pptx_output = os.path.join(tempfile.gettempdir(), "test_output.pptx")
try:
    result = pdf_to_powerpoint(test_pdf_path, pptx_output)
    if result:
        print(f"[OK] PDF to PowerPoint conversion succeeded")
        print(f"  Output file: {pptx_output}")
        print(f"  File exists: {os.path.exists(pptx_output)}")
        print(f"  File size: {os.path.getsize(pptx_output)} bytes")
    else:
        print("[ERROR] PDF to PowerPoint conversion returned False")
except Exception as e:
    print(f"[ERROR] PDF to PowerPoint conversion failed: {e}")
    import traceback
    traceback.print_exc()

# Test powerpoint_to_pdf
print("\n--- Testing powerpoint_to_pdf ---")
if os.path.exists(pptx_output):
    pdf_output = os.path.join(tempfile.gettempdir(), "test_output.pdf")
    try:
        result = powerpoint_to_pdf(pptx_output, pdf_output)
        if result:
            print(f"[OK] PowerPoint to PDF conversion succeeded")
            print(f"  Output file: {pdf_output}")
            print(f"  File exists: {os.path.exists(pdf_output)}")
            print(f"  File size: {os.path.getsize(pdf_output)} bytes")
        else:
            print("[ERROR] PowerPoint to PDF conversion returned False")
    except Exception as e:
        print(f"[ERROR] PowerPoint to PDF conversion failed: {e}")
        import traceback
        traceback.print_exc()

print("\n--- Test Complete ---")
