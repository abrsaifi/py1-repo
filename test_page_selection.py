#!/usr/bin/env python3
"""
Test page selection functionality for watermarks.
"""

import sys
from pathlib import Path
import tempfile
import os

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def test_page_selection():
    """Test watermark on selected pages."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import server
    
    print("=" * 70)
    print("TESTING PAGE SELECTION FOR WATERMARKS")
    print("=" * 70)
    print()
    
    results = []
    
    # Test cases for page selection
    test_cases = [
        {
            'name': 'All Pages (None)',
            'pages': None,
            'expected_watermarked': [0, 1, 2]
        },
        {
            'name': 'Only Page 1',
            'pages': [0],
            'expected_watermarked': [0]
        },
        {
            'name': 'Pages 1 and 3',
            'pages': [0, 2],
            'expected_watermarked': [0, 2]
        },
        {
            'name': 'Pages 2-3 (Range)',
            'pages': [1, 2],
            'expected_watermarked': [1, 2]
        }
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a 3-page test PDF
        test_pdf = os.path.join(tmpdir, 'test.pdf')
        c = canvas.Canvas(test_pdf, pagesize=letter)
        
        for page_num in range(3):
            c.drawString(100, 750, f"Page {page_num + 1}")
            c.showPage()
        
        c.save()
        
        print(f"Created 3-page test PDF\n")
        
        for test_case in test_cases:
            try:
                output_pdf = os.path.join(tmpdir, f'watermark_{test_case["name"].replace(" ", "_")}.pdf')
                
                result = server.add_watermark(
                    test_pdf, 
                    output_pdf, 
                    "TEST",
                    opacity=0.3,
                    position='center',
                    font_size=40,
                    color=(0, 0, 0),
                    fontname='helv',
                    pages=test_case['pages']
                )
                
                if result and os.path.exists(output_pdf):
                    size = os.path.getsize(output_pdf)
                    pages_str = test_case['pages'] if test_case['pages'] else 'All'
                    print(f"[OK] {test_case['name']:30} - Created (size: {size} bytes)")
                    results.append(True)
                else:
                    print(f"[FAIL] {test_case['name']:30} - Failed to create")
                    results.append(False)
            except Exception as e:
                print(f"[FAIL] {test_case['name']:30} - Error: {str(e)[:40]}")
                results.append(False)
    
    print()
    print("=" * 70)
    print("TESTING PAGE NUMBER PARSING")
    print("=" * 70)
    print()
    
    parse_tests = [
        {
            'input': '1, 3, 5',
            'expected': [0, 2, 4],
            'name': 'Comma-separated'
        },
        {
            'input': '1 3 5',
            'expected': [0, 2, 4],
            'name': 'Space-separated'
        },
        {
            'input': '1-3, 5',
            'expected': [0, 1, 2, 4],
            'name': 'Range + single'
        },
        {
            'input': '5-8',
            'expected': [4, 5, 6, 7],
            'name': 'Range only'
        },
        {
            'input': '2, 4-6, 8',
            'expected': [1, 3, 4, 5, 7],
            'name': 'Mixed format'
        }
    ]
    
    for test in parse_tests:
        try:
            result = server.parse_page_numbers(test['input'])
            if result == test['expected']:
                print(f"[OK] {test['name']:30} - Parse OK")
                results.append(True)
            else:
                print(f"[FAIL] {test['name']:30} - Expected {test['expected']}, got {result}")
                results.append(False)
        except Exception as e:
            print(f"[FAIL] {test['name']:30} - Error: {str(e)[:40]}")
            results.append(False)
    
    print()
    print("=" * 70)
    if all(results):
        print("[SUCCESS] ALL PAGE SELECTION TESTS PASSED!")
        print()
        print("Page selection features added:")
        print("  - All pages mode (None)")
        print("  - Selected pages mode with flexible input formats")
        print("  - Support for comma and space separators")
        print("  - Support for page ranges (e.g., 5-8)")
        print("  - Mixed format support (e.g., 1, 3-5, 8)")
    else:
        print("[FAILED] Some page selection tests failed")
    assert all(results), "Some page selection tests failed"

if __name__ == '__main__':
    try:
        test_page_selection()
        sys.exit(0)
    except AssertionError:
        sys.exit(1)
