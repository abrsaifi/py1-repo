#!/usr/bin/env python3
"""
Test enhanced watermark functionality with new settings.
"""

import sys
from pathlib import Path
import tempfile
import os

repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def test_enhanced_watermark():
    """Test watermark with enhanced settings."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import server
    
    print("=" * 70)
    print("TESTING ENHANCED WATERMARK FUNCTIONALITY")
    print("=" * 70)
    print()
    
    results = []
    
    # Test configurations
    test_configs = [
        {
            'name': 'Default (Gray, 50pt)',
            'kwargs': {
                'font_size': 50,
                'color': (0.5, 0.5, 0.5),
                'fontname': 'helv',
                'position': 'diagonal'
            }
        },
        {
            'name': 'Black Large (80pt)',
            'kwargs': {
                'font_size': 80,
                'color': (0, 0, 0),
                'fontname': 'times-roman',
                'position': 'center'
            }
        },
        {
            'name': 'Red Bold (70pt)',
            'kwargs': {
                'font_size': 70,
                'color': (1, 0, 0),
                'fontname': 'courier',
                'position': 'top'
            }
        },
        {
            'name': 'Blue Small (30pt)',
            'kwargs': {
                'font_size': 30,
                'color': (0, 0, 1),
                'fontname': 'helv',
                'position': 'bottom'
            }
        },
        {
            'name': 'First Page Only',
            'kwargs': {
                'font_size': 60,
                'color': (0.5, 0.5, 0.5),
                'fontname': 'helv',
                'position': 'diagonal',
                'all_pages': False
            }
        }
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a multi-page test PDF
        test_pdf = os.path.join(tmpdir, 'test.pdf')
        c = canvas.Canvas(test_pdf, pagesize=letter)
        
        # Page 1
        c.drawString(100, 750, "Page 1: Test Document for Enhanced Watermark")
        c.drawString(100, 700, "This is the first page")
        c.showPage()
        
        # Page 2
        c.drawString(100, 750, "Page 2: More Content")
        c.drawString(100, 700, "This is the second page")
        c.showPage()
        
        # Page 3
        c.drawString(100, 750, "Page 3: Additional Content")
        c.drawString(100, 700, "This is the third page")
        c.save()
        
        print(f"Created multi-page test PDF: {test_pdf}\n")
        
        for i, config in enumerate(test_configs, 1):
            try:
                output_pdf = os.path.join(tmpdir, f'watermark_test_{i}.pdf')
                kwargs = config['kwargs'].copy()
                
                result = server.add_watermark(
                    test_pdf, 
                    output_pdf, 
                    "WATERMARK",
                    opacity=0.3,
                    **kwargs
                )
                
                if result and os.path.exists(output_pdf):
                    size = os.path.getsize(output_pdf)
                    print(f"[{i}] {config['name']:30} - OK (size: {size} bytes)")
                    results.append(True)
                else:
                    print(f"[{i}] {config['name']:30} - Failed")
                    results.append(False)
            except Exception as e:
                print(f"[{i}] {config['name']:30} - Error: {str(e)[:40]}")
                results.append(False)
    
    print()
    print("=" * 70)
    if all(results):
        print("[SUCCESS] ALL ENHANCED WATERMARK TESTS PASSED!")
        print()
        print("New watermark settings added:")
        print("  - Multiple font options (Helvetica, Times Roman, Courier)")
        print("  - Adjustable font size (20-120pt)")
        print("  - Custom colors (Gray, Black, Red, Blue, Green)")
        print("  - Apply to all pages or first page only")
        print("  - Opacity control (0.1-0.9)")
        return 0
    else:
        print("[FAILED] Some enhanced watermark tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(test_enhanced_watermark())
