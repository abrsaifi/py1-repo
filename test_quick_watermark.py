#!/usr/bin/env python3
"""
Quick verification that all watermark functionality works together.
"""

import sys
from pathlib import Path
import tempfile
import os

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def quick_test():
    """Quick test of watermark with page selection."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import server
    
    print("[Testing] Creating test PDF...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_pdf = os.path.join(tmpdir, 'test.pdf')
        c = canvas.Canvas(test_pdf, pagesize=letter)
        
        for i in range(3):
            c.drawString(100, 750, f"Page {i+1}")
            c.showPage()
        
        c.save()
        
        # Test 1: All pages
        print("[Test 1] All pages watermark...", end=" ")
        output1 = os.path.join(tmpdir, 'all_pages.pdf')
        if server.add_watermark(test_pdf, output1, "TEST", pages=None):
            print("OK")
        else:
            print("FAIL")
            return False
        
        # Test 2: Selected pages
        print("[Test 2] Selected pages (1,3)...", end=" ")
        output2 = os.path.join(tmpdir, 'selected_pages.pdf')
        if server.add_watermark(test_pdf, output2, "TEST", pages=[0, 2]):
            print("OK")
        else:
            print("FAIL")
            return False
        
        # Test 3: Parse page input
        print("[Test 3] Parse '1, 3, 5-7'...", end=" ")
        parsed = server.parse_page_numbers('1, 3, 5-7')
        if parsed == [0, 2, 4, 5, 6]:
            print("OK")
        else:
            print(f"FAIL (got {parsed})")
            return False
        
        # Test 4: Enhanced settings with page selection
        print("[Test 4] Enhanced settings + page selection...", end=" ")
        output3 = os.path.join(tmpdir, 'enhanced.pdf')
        if server.add_watermark(
            test_pdf, output3, "CONFIDENTIAL",
            opacity=0.5,
            position='diagonal',
            font_size=70,
            color=(1, 0, 0),
            fontname='times-roman',
            pages=[1]
        ):
            print("OK")
        else:
            print("FAIL")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("QUICK WATERMARK + PAGE SELECTION TEST")
    print("=" * 60)
    print()
    
    if quick_test():
        print()
        print("=" * 60)
        print("[SUCCESS] All watermark features working correctly!")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("[FAILED] Some tests failed")
        sys.exit(1)
