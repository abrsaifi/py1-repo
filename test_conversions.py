#!/usr/bin/env python3
"""
Comprehensive test script to verify all conversion tasks are working well.
"""

import sys
from pathlib import Path
import tempfile
import os

VERBOSE = __name__ == '__main__'


def log(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

def test_imports():
    """Test if all required modules can be imported."""
    log("=" * 70)
    log("TESTING MODULE IMPORTS")
    log("=" * 70)
    
    required_modules = [
        'flask',
        'PIL',
        'fitz',
        'pdfplumber',
        'pypdf',
        'openpyxl',
        'docx',
        'reportlab',
        'pdf2image',
        'img2pdf',
        'easyocr',
        'pandas',
        'numpy',
        'cv2',
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            log(f"✓ {module:25} - OK")
        except ImportError as e:
            log(f"✗ {module:25} - FAILED: {e}")
            failed_imports.append(module)
    
    log()
    assert not failed_imports, f"Missing required imports: {failed_imports}"


def test_server_functions():
    """Test if server.py has all required conversion functions."""
    log("=" * 70)
    log("TESTING SERVER CONVERSION FUNCTIONS")
    log("=" * 70)
    
    try:
        import server
    except ImportError as e:
        log(f"✗ Could not import server module: {e}")
        raise AssertionError(f"Could not import server module: {e}") from e
    
    required_functions = [
        'image_to_pdf',
        'docx_to_pdf',
        'excel_to_pdf',
        'pdf_to_word',
        'pdf_to_excel',
        'pdf_to_true_bw',
        'ocr_extract_text',
        'add_watermark',
        'encrypt_pdf',
        'decrypt_pdf',
        'clean_autoformat_pdf',
        'excel_to_csv',
        'split_pdf',
        'merge_pdf',
    ]
    
    missing_functions = []
    for func_name in required_functions:
        if hasattr(server, func_name):
            log(f"✓ {func_name:30} - OK")
        else:
            log(f"✗ {func_name:30} - MISSING")
            missing_functions.append(func_name)
    
        log()
    assert not missing_functions, f"Missing server functions: {missing_functions}"


def test_helper_modules():
    """Test if helper modules can be imported and have required functions."""
    log("=" * 70)
    log("TESTING HELPER MODULES")
    log("=" * 70)
    
    all_ok = True
    
    # Test pdf_handler
    try:
        from pdf_handler import pdf_to_images, images_to_pdf
        log("✓ pdf_handler.py            - pdf_to_images, images_to_pdf")
    except ImportError as e:
        log(f"✗ pdf_handler.py            - FAILED: {e}")
        all_ok = False
    
    # Test image_processor
    try:
        from image_processor import convert_to_bw, process_images_to_bw
        log("✓ image_processor.py        - convert_to_bw, process_images_to_bw")
    except ImportError as e:
        log(f"✗ image_processor.py        - FAILED: {e}")
        all_ok = False
    
    # Test file_utils
    try:
        from file_utils import save_images_to_temp, cleanup_temp_files
        log("✓ file_utils.py             - save_images_to_temp, cleanup_temp_files")
    except ImportError as e:
        log(f"✗ file_utils.py             - FAILED: {e}")
        all_ok = False
    
    log()
    assert all_ok, "One or more helper modules failed to import"


def test_basic_conversions():
    """Test basic conversion functionality by creating simple test files."""
    log("=" * 70)
    log("TESTING BASIC CONVERSION FUNCTIONALITY")
    log("=" * 70)
    
    try:
        from PIL import Image
        import server
        import tempfile
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            test_results = []
            
            # Test 1: Image to PDF
            try:
                img = Image.new('RGB', (200, 200), color='red')
                test_img_path = os.path.join(tmpdir, 'test.png')
                img.save(test_img_path)
                test_pdf_path = os.path.join(tmpdir, 'test_from_img.pdf')
                
                result = server.image_to_pdf(test_img_path, test_pdf_path)
                if os.path.exists(test_pdf_path):
                    log(f"✓ image_to_pdf              - OK")
                    test_results.append(True)
                else:
                    log(f"✗ image_to_pdf              - Failed to create output file")
                    test_results.append(False)
            except Exception as e:
                log(f"✗ image_to_pdf              - Error: {str(e)[:50]}")
                test_results.append(False)
            
            # Test 2: PDF to True BW
            try:
                # Create a simple test PDF first
                test_pdf_path = os.path.join(tmpdir, 'test_source.pdf')
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                c = canvas.Canvas(test_pdf_path, pagesize=letter)
                c.drawString(100, 750, "Test PDF for BW conversion")
                c.save()
                
                output_bw_path = os.path.join(tmpdir, 'test_bw.pdf')
                result = server.pdf_to_true_bw(test_pdf_path, output_bw_path)
                
                if result and os.path.exists(output_bw_path):
                    log(f"✓ pdf_to_true_bw            - OK")
                    test_results.append(True)
                else:
                    log(f"✗ pdf_to_true_bw            - Failed")
                    test_results.append(False)
            except Exception as e:
                log(f"✗ pdf_to_true_bw            - Error: {str(e)[:50]}")
                test_results.append(False)
            
            # Test 3: Image Processor (BW conversion)
            try:
                from image_processor import convert_to_bw
                img = Image.new('RGB', (100, 100), color='gray')
                bw_img = convert_to_bw(img, threshold=128)
                if bw_img is not None:
                    log(f"✓ image_processor (B&W)     - OK")
                    test_results.append(True)
                else:
                    log(f"✗ image_processor (B&W)     - Failed")
                    test_results.append(False)
            except Exception as e:
                log(f"✗ image_processor (B&W)     - Error: {str(e)[:50]}")
                test_results.append(False)
            
            log()
            assert all(test_results), "One or more basic conversion checks failed"
        
    except Exception as e:
        log(f"✗ Basic conversion tests    - Error: {e}")
        log()
        raise AssertionError(f"Basic conversion tests failed: {e}") from e


def test_app_routes():
    """Test if Flask app routes are properly defined."""
    log("=" * 70)
    log("TESTING FLASK APP ROUTES")
    log("=" * 70)
    
    try:
        import server
        
        required_routes = [
            '/',
            '/convert',
            '/convert-to-pdf',
            '/pdf-extract',
            '/ocr',
            '/watermark',
            '/encrypt',
            '/autoformat',
            '/excel-to-csv',
            '/split-pdf',
            '/merge-pdf',
            '/remove-pdf-pages',
            '/decrypt-pdf',
            '/history-data',
        ]
        
        app = server.app
        registered_routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        missing_routes = []
        for route in required_routes:
            if route in registered_routes:
                log(f"✓ {route:25} - OK")
            else:
                log(f"✗ {route:25} - NOT FOUND")
                missing_routes.append(route)
        
        log()
        assert not missing_routes, f"Missing routes: {missing_routes}"
        
    except Exception as e:
        log(f"✗ Error checking routes: {e}")
        log()
        raise AssertionError(f"Error checking routes: {e}") from e


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "CONVERSION TASKS VERIFICATION TEST SUITE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    test_cases = [
        ('Module Imports', test_imports),
        ('Server Functions', test_server_functions),
        ('Helper Modules', test_helper_modules),
        ('Basic Conversions', test_basic_conversions),
        ('Flask Routes', test_app_routes),
    ]
    results = {}
    for test_name, test_func in test_cases:
        try:
            test_func()
            results[test_name] = True
        except AssertionError:
            results[test_name] = False
    
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:30} {status}")
    
    print()
    
    all_passed = all(results.values())
    if all_passed:
        print("╔" + "=" * 68 + "╗")
        print("║" + "ALL TESTS PASSED! ✓".center(68) + "║")
        print("║" + "All conversion tasks are working well!".center(68) + "║")
        print("╚" + "=" * 68 + "╝")
        return 0
    else:
        print("╔" + "=" * 68 + "╗")
        print("║" + "SOME TESTS FAILED! ✗".center(68) + "║")
        print("║" + "Please review the failures above".center(68) + "║")
        print("╚" + "=" * 68 + "╝")
        return 1


if __name__ == '__main__':
    sys.exit(main())
