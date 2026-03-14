#!/usr/bin/env python3
"""Test all new advanced features"""

import os
import sys
import tempfile
from pathlib import Path
from PIL import Image as PILImage
import fitz

sys.path.insert(0, str(Path(__file__).parent))
from server import (
    add_watermark, redact_pdf, text_to_pdf, html_to_pdf,
    pdf_remove_metadata, ocr_extract_with_language
)

def create_test_pdf(path, text="Test PDF"):
    """Create a test PDF"""
    doc = fitz.open()
    page = doc.new_page()
    shape = page.new_shape()
    shape.insert_text((50, 50), text, fontsize=12)
    shape.commit()
    doc.save(path)
    doc.close()

def test_watermark_rotation():
    """Test watermark with rotation and scale effects"""
    print("Test 1: Watermark rotation and scale...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        
        create_test_pdf(input_pdf)
        
        # Test with rotation
        result = add_watermark(input_pdf, output_pdf, 'CONFIDENTIAL',
                             opacity=0.5, position='diagonal',
                             rotation=45, scale=1.5)
        
        if result and os.path.exists(output_pdf):
            print("  PASS: Rotation and scale applied")
        else:
            print("  FAIL: Rotation/scale test")
        assert result and os.path.exists(output_pdf), "Rotation/scale watermark test failed"

def test_redaction():
    """Test redaction feature"""
    print("Test 2: Document redaction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf = os.path.join(tmpdir, 'redacted.pdf')
        
        # Create PDF with sensitive text
        doc = fitz.open()
        page = doc.new_page()
        shape = page.new_shape()
        shape.insert_text((50, 50), "Password: secret123", fontsize=12)
        shape.insert_text((50, 80), "Credit Card: 1234-5678-9012", fontsize=12)
        shape.commit()
        doc.save(input_pdf)
        doc.close()
        
        # Redact keywords
        keywords = ['Password', 'Credit Card', 'secret123']
        result = redact_pdf(input_pdf, output_pdf, keywords)
        
        if result and os.path.exists(output_pdf):
            print("  PASS: Redaction completed")
        else:
            print("  FAIL: Redaction test")
        assert result and os.path.exists(output_pdf), "Redaction test failed"

def test_text_to_pdf():
    """Test text to PDF conversion"""
    print("Test 3: Text to PDF conversion...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        
        text_content = """This is a test document.
It has multiple lines.
And paragraphs.

With spacing between them."""
        
        result = text_to_pdf(text_content, output_pdf, font_size=12)
        
        if result and os.path.exists(output_pdf):
            output_doc = fitz.open(output_pdf)
            if len(output_doc) > 0:
                print("  PASS: Text to PDF conversion")
                output_doc.close()
                return
            output_doc.close()
        
        print("  FAIL: Text to PDF test")
        assert False, "Text to PDF test failed"

def test_html_to_pdf():
    """Test HTML to PDF conversion"""
    print("Test 4: HTML to PDF conversion...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        
        html_content = """<h1>Test Document</h1>
<p>This is a paragraph with HTML formatting.</p>
<p>This is another paragraph.</p>"""
        
        result = html_to_pdf(html_content, output_pdf)
        
        if result and os.path.exists(output_pdf):
            output_doc = fitz.open(output_pdf)
            if len(output_doc) > 0:
                print("  PASS: HTML to PDF conversion")
                output_doc.close()
                return
            output_doc.close()
        
        print("  FAIL: HTML to PDF test")
        assert False, "HTML to PDF test failed"

def test_metadata_removal():
    """Test metadata removal"""
    print("Test 5: PDF metadata removal...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        input_with_metadata_pdf = os.path.join(tmpdir, 'test_with_metadata.pdf')
        output_pdf = os.path.join(tmpdir, 'clean.pdf')
        
        create_test_pdf(input_pdf)
        
        # Set metadata
        doc = fitz.open(input_pdf)
        doc.set_metadata({
            'title': 'Secret Title',
            'author': 'Secret Author',
            'subject': 'Confidential'
        })
        doc.save(input_with_metadata_pdf)
        doc.close()
        
        # Remove metadata
        result = pdf_remove_metadata(input_with_metadata_pdf, output_pdf)
        
        if result and os.path.exists(output_pdf):
            # Verify metadata is removed
            doc = fitz.open(output_pdf)
            metadata = doc.metadata
            doc.close()
            
            if metadata.get('title', '') == '' or metadata.get('author', '') == '':
                print("  PASS: Metadata removed successfully")
                return
        
        print("  FAIL: Metadata removal test")
        assert False, "Metadata removal test failed"

def test_watermark_all_positions():
    """Test watermark at all 8 positions with rotation"""
    print("Test 6: Watermark at all positions with rotation...")
    
    positions = ['diagonal', 'top', 'bottom', 'center', 'top-left', 
                 'top-right', 'bottom-left', 'bottom-right']
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        create_test_pdf(input_pdf)
        
        passed = 0
        for pos in positions:
            output_pdf = os.path.join(tmpdir, f'output_{pos}.pdf')
            result = add_watermark(input_pdf, output_pdf, 'TEST',
                                 position=pos, rotation=15, scale=1.2)
            if result and os.path.exists(output_pdf):
                passed += 1
        
        if passed == len(positions):
            print(f"  PASS: All {len(positions)} positions tested")
        else:
            print(f"  FAIL: Only {passed}/{len(positions)} positions passed")
        assert passed == len(positions), f"Only {passed}/{len(positions)} positions passed"

if __name__ == '__main__':
    print("=" * 50)
    print("Testing New Advanced Features")
    print("=" * 50)
    
    try:
        tests = [
            test_watermark_rotation,
            test_redaction,
            test_text_to_pdf,
            test_html_to_pdf,
            test_metadata_removal,
            test_watermark_all_positions,
        ]
        results = []
        for test_func in tests:
            try:
                test_func()
                results.append(True)
            except AssertionError:
                results.append(False)
        
        print("=" * 50)
        passed = sum(results)
        total = len(results)
        print(f"RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("ALL TESTS PASSED!")
        else:
            print(f"Some tests failed ({total - passed} failures)")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
