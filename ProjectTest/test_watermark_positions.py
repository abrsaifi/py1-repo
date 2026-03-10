#!/usr/bin/env python3
"""
Test watermark functionality with different positions and settings.
"""

import sys
from pathlib import Path
import tempfile
import os

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def test_watermark_positions():
    """Test watermark with different positions."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import server
    
    print("=" * 70)
    print("TESTING WATERMARK WITH DIFFERENT POSITIONS")
    print("=" * 70)
    print()
    
    results = []
    
    positions = ['diagonal', 'top', 'bottom', 'center']
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test PDF
        test_pdf = os.path.join(tmpdir, 'test.pdf')
        c = canvas.Canvas(test_pdf, pagesize=letter)
        c.drawString(100, 750, "Test Document for Watermark")
        c.drawString(100, 700, "This is a sample PDF to test watermark functionality")
        c.save()
        
        print(f"Created test PDF: {test_pdf}\n")
        
        for position in positions:
            try:
                output_pdf = os.path.join(tmpdir, f'watermark_{position}.pdf')
                
                result = server.add_watermark(
                    test_pdf, 
                    output_pdf, 
                    "CONFIDENTIAL",
                    opacity=0.3,
                    position=position
                )
                
                if result and os.path.exists(output_pdf):
                    size = os.path.getsize(output_pdf)
                    print(f"[OK] Position '{position:10}' - OK (size: {size} bytes)")
                    results.append(True)
                else:
                    print(f"[FAIL] Position '{position:10}' - Failed")
                    results.append(False)
            except Exception as e:
                print(f"[FAIL] Position '{position:10}' - Error: {str(e)[:40]}")
                results.append(False)
    
    print()
    print("=" * 70)
    if all(results):
        print("[SUCCESS] ALL WATERMARK TESTS PASSED!")
        print("  Watermark functionality is now working correctly.")
        return 0
    else:
        print("[FAILED] Some watermark tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(test_watermark_positions())
