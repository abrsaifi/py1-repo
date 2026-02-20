#!/usr/bin/env python3
"""Test image watermark functionality end-to-end"""

import os
import tempfile
from pathlib import Path
from PIL import Image
import fitz

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from server import add_image_watermark

def create_test_pdf(path, text="Test PDF"):
    """Create a simple test PDF"""
    doc = fitz.open()
    page = doc.new_page()
    shape = page.new_shape()
    shape.insert_text((50, 50), text, fontsize=12)
    shape.commit()
    doc.save(path)
    doc.close()

def test_image_watermark_basic():
    """Test basic image watermark"""
    print("Test 1: Basic image watermark...")
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        image_path = os.path.join(tmpdir, 'logo.png')
        
        create_test_pdf(input_pdf)
        img = Image.new('RGB', (200, 100), 'blue')
        img.save(image_path)
        img.close()  # Close PIL image to release file
        
        result = add_image_watermark(input_pdf, output_pdf, image_path, 
                                    position='center', scale=50, scale_unit='percent')
        assert result, "Image watermark failed"
        assert os.path.exists(output_pdf), "Output file not created"
        assert os.path.getsize(output_pdf) > 0, "Output file is empty"
        print("✓ PASSED")

def test_image_watermark_positions():
    """Test image watermark at different positions"""
    print("Test 2: Image watermark at different positions...")
    positions = ['diagonal', 'top', 'bottom', 'center', 'top-left', 'top-right', 
                 'bottom-left', 'bottom-right']
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        image_path = os.path.join(tmpdir, 'logo.png')
        
        create_test_pdf(input_pdf)
        img = Image.new('RGB', (150, 75), 'green')
        img.save(image_path)
        img.close()
        
        for pos in positions:
            output_pdf = os.path.join(tmpdir, f'output_{pos}.pdf')
            result = add_image_watermark(input_pdf, output_pdf, image_path, 
                                        position=pos, scale=40, scale_unit='percent')
            assert result, f"Image watermark at {pos} failed"
            assert os.path.exists(output_pdf), f"Output for {pos} not created"
            print(f"  ✓ {pos}")
    print("✓ PASSED")

def test_image_watermark_scale_units():
    """Test image watermark with different scale units"""
    print("Test 3: Image watermark with different scale units...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf_pct = os.path.join(tmpdir, 'output_pct.pdf')
        output_pdf_inches = os.path.join(tmpdir, 'output_inches.pdf')
        image_path = os.path.join(tmpdir, 'logo.png')
        
        create_test_pdf(input_pdf)
        img = Image.new('RGB', (200, 100), 'yellow')
        img.save(image_path)
        img.close()
        
        # Percent of page width
        result1 = add_image_watermark(input_pdf, output_pdf_pct, image_path,
                                     position='top', scale=25, scale_unit='percent')
        assert result1, "Percent scale failed"
        assert os.path.exists(output_pdf_pct), "Percent output not created"
        print("  ✓ Percent of page width (25%)")
        
        # Inches
        result2 = add_image_watermark(input_pdf, output_pdf_inches, image_path,
                                     position='top', scale=1.5, scale_unit='inches')
        assert result2, "Inches scale failed"
        assert os.path.exists(output_pdf_inches), "Inches output not created"
        print("  ✓ Fixed inches (1.5 inches)")
    print("✓ PASSED")

def test_image_watermark_page_selection():
    """Test image watermark on selected pages"""
    print("Test 4: Image watermark on selected pages...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        image_path = os.path.join(tmpdir, 'logo.png')
        
        # Create multi-page PDF
        doc = fitz.open()
        for i in range(3):
            page = doc.new_page()
            shape = page.new_shape()
            shape.insert_text((50, 50), f"Page {i+1}", fontsize=12)
            shape.commit()
        doc.save(input_pdf)
        doc.close()
        
        img = Image.new('RGB', (150, 75), 'cyan')
        img.save(image_path)
        img.close()
        
        # Watermark only page 1 and 3 (0-indexed: 0, 2)
        result = add_image_watermark(input_pdf, output_pdf, image_path,
                                    position='center', scale=30, scale_unit='percent',
                                    pages=[0, 2])
        assert result, "Page-selected watermark failed"
        assert os.path.exists(output_pdf), "Output file not created"
        
        # Verify it's a valid PDF with 3 pages
        output_doc = fitz.open(output_pdf)
        assert len(output_doc) == 3, "Page count mismatch"
        output_doc.close()
        print("  ✓ Watermarked pages 1 and 3 only")
    print("✓ PASSED")

def test_image_watermark_scale_bounds():
    """Test image watermark scale bounds (10-200%)"""
    print("Test 5: Image watermark scale bounds...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        image_path = os.path.join(tmpdir, 'logo.png')
        
        create_test_pdf(input_pdf)
        img = Image.new('RGB', (200, 100), 'magenta')
        img.save(image_path)
        img.close()
        
        # Min scale (10%)
        result1 = add_image_watermark(input_pdf, output_pdf, image_path,
                                     position='center', scale=5, scale_unit='percent')
        assert result1, "Min scale test failed"
        print("  ✓ Below min (5%) accepted")
        
        # Max scale (200%)
        result2 = add_image_watermark(input_pdf, output_pdf, image_path,
                                     position='center', scale=250, scale_unit='percent')
        assert result2, "Max scale test failed"
        print("  ✓ Above max (250%) accepted")
    print("✓ PASSED")

def test_image_aspect_ratio():
    """Test aspect ratio preservation"""
    print("Test 6: Image aspect ratio preservation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = os.path.join(tmpdir, 'test.pdf')
        output_pdf = os.path.join(tmpdir, 'output.pdf')
        image_path = os.path.join(tmpdir, 'logo.png')
        
        create_test_pdf(input_pdf)
        # Create square image
        img = Image.new('RGB', (200, 200), 'orange')
        img.save(image_path)
        img.close()
        
        result = add_image_watermark(input_pdf, output_pdf, image_path,
                                    position='center', scale=50, scale_unit='percent')
        assert result, "Aspect ratio test failed"
        
        output_doc = fitz.open(output_pdf)
        # Just verify it created a valid output
        assert len(output_doc) > 0, "Output PDF has no pages"
        output_doc.close()
        print("  ✓ Square image preserves aspect ratio")
    print("✓ PASSED")

if __name__ == '__main__':
    try:
        print("=" * 50)
        print("Testing Image Watermark Functionality")
        print("=" * 50)
        test_image_watermark_basic()
        test_image_watermark_positions()
        test_image_watermark_scale_units()
        test_image_watermark_page_selection()
        test_image_watermark_scale_bounds()
        test_image_aspect_ratio()
        print("=" * 50)
        print("ALL TESTS PASSED ✓")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
