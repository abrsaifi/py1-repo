#!/usr/bin/env python3
"""
Test watermark functionality to identify issues.
"""

import sys
from pathlib import Path
import tempfile
import os

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def test_watermark():
    """Test the watermark function."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import server
    
    print("=" * 70)
    print("TESTING WATERMARK FUNCTIONALITY")
    print("=" * 70)
    print()
    
    try:
        # Create a test PDF
        with tempfile.TemporaryDirectory() as tmpdir:
            test_pdf = os.path.join(tmpdir, 'test.pdf')
            c = canvas.Canvas(test_pdf, pagesize=letter)
            c.drawString(100, 750, "Test Document")
            c.save()
            
            output_pdf = os.path.join(tmpdir, 'watermarked.pdf')
            
            print("Creating test PDF...")
            print(f"Test PDF: {test_pdf}")
            
            print("Testing add_watermark function...")
            result = server.add_watermark(test_pdf, output_pdf, "CONFIDENTIAL", opacity=0.3, position='diagonal')
            
            if result:
                print("✓ Watermark function executed")
                if os.path.exists(output_pdf):
                    print(f"✓ Output file created: {output_pdf}")
                    size = os.path.getsize(output_pdf)
                    print(f"✓ Output file size: {size} bytes")
                else:
                    print("✗ Output file was not created")
            else:
                print("✗ Watermark function returned False")
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_watermark()
