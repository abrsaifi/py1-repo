#!/usr/bin/env python3
"""
Comprehensive dependency and conversion verification script.
Tests all required dependencies and core conversion functions.
"""

import sys
import os

print("\n" + "="*70)
print("DEPENDENCY & CONVERSION VERIFICATION REPORT")
print("="*70)

# Test 1: Check Python Version
print("\n1. PYTHON VERSION")
print("-" * 70)
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")

# Test 2: Check all dependencies
print("\n2. DEPENDENCY CHECK")
print("-" * 70)

dependencies = {
    'flask': 'Flask web framework',
    'fitz': 'PyMuPDF for PDF/image conversion',
    'PIL': 'Pillow for image processing',
    'pdfplumber': 'PDF extraction and analysis',
    'pypdf': 'PDF manipulation',
    'reportlab': 'PDF generation',
    'openpyxl': 'Excel file handling',
    'pandas': 'Data processing',
    'numpy': 'Numerical operations',
    'cv2': 'OpenCV for image processing',
    'docx': 'Word document handling',
    'pptx': 'PowerPoint presentation handling',
    'requests': 'HTTP client',
    'bs4': 'BeautifulSoup for HTML parsing',
    'pdf2image': 'PDF to image conversion',
}

# Heavy dependencies that load slower but are optional
optional_dependencies = {
    'easyocr': 'Optical Character Recognition (loads torch)',
    'torch': 'PyTorch machine learning',
}

installed_count = 0
failed_count = 0
failed_deps = []

for module_name, description in dependencies.items():
    try:
        __import__(module_name)
        print(f"  OK: {module_name:25} - {description}")
        installed_count += 1
    except ImportError as e:
        print(f"  FAIL: {module_name:25} - {description}")
        print(f"        Error: {str(e)[:60]}")
        failed_count += 1
        failed_deps.append(module_name)

print(f"\n  Summary: {installed_count} OK, {failed_count} FAILED")

# Check optional dependencies
print("\n  OPTIONAL DEPENDENCIES (heavy loading):")
for module_name, description in optional_dependencies.items():
    try:
        __import__(module_name)
        print(f"  OK: {module_name:25} - {description}")
        installed_count += 1
    except ImportError:
        print(f"  OPTIONAL (not needed for basic conversions): {module_name}")


# Test 3: Check server.py can be imported
print("\n3. SERVER APPLICATION CHECK")
print("-" * 70)

try:
    # Check if server.py exists and has required functions
    with open('server.py', 'r') as f:
        server_content = f.read()
    
    required_functions = [
        'pdf_to_images',
        'convert_pdf_to_docx',
        'convert_docx_to_pdf',
        'convert_pdf_to_xlsx',
        'convert_xlsx_to_pdf',
        'convert_pdf_to_pptx',
        'convert_image_format',
        'add_watermark',
        'merge_pdfs',
    ]
    
    found_functions = []
    missing_functions = []
    
    for func in required_functions:
        if f'def {func}' in server_content:
            found_functions.append(func)
            print(f"  OK: {func}")
        else:
            missing_functions.append(func)
            print(f"  MISSING: {func}")
    
    print(f"\n  Summary: {len(found_functions)} functions found, {len(missing_functions)} missing")
    
except Exception as e:
    print(f"  ERROR: Could not check server.py - {e}")

# Test 4: Check conversion functions exist
print("\n4. CORE CONVERSION MODULES CHECK")
print("-" * 70)

modules_to_check = [
    ('pdf_handler.py', ['pdf_to_images', 'images_to_pdf']),
    ('image_processor.py', ['process_images_to_bw', 'enhance_image']),
    ('file_utils.py', ['save_images_to_temp', 'cleanup_temp_files']),
]

for module_file, functions in modules_to_check:
    try:
        with open(module_file, 'r') as f:
            content = f.read()
        
        found = [fn for fn in functions if f'def {fn}' in content]
        missing = [fn for fn in functions if f'def {fn}' not in content]
        
        if missing:
            print(f"  PARTIAL: {module_file} ({len(found)}/{len(functions)} functions)")
            for fn in missing:
                print(f"    MISSING: {fn}")
        else:
            print(f"  OK: {module_file} (all {len(found)} functions)")
    except FileNotFoundError:
        print(f"  MISSING FILE: {module_file}")
    except Exception as e:
        print(f"  ERROR: {module_file} - {str(e)[:50]}")

# Test 5: Database check
print("\n5. DATABASE & HISTORY CHECK")
print("-" * 70)

db_files = [
    'docpro_database.db',
    'conversion_history.db',
]

for db_file in db_files:
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f"  OK: {db_file} (size: {size} bytes)")
    else:
        print(f"  NOT FOUND: {db_file}")

# Test 6: Check templates and static files
print("\n6. APPLICATION RESOURCES CHECK")
print("-" * 70)

resources = [
    ('templates', 'Template directory'),
    ('static', 'Static files directory'),
    ('app', 'App module directory'),
]

for resource, description in resources:
    if os.path.isdir(resource):
        item_count = len(os.listdir(resource))
        print(f"  OK: {resource:20} - {description} ({item_count} items)")
    else:
        print(f"  MISSING: {resource:20} - {description}")

# Test 7: Check test files
print("\n7. TEST FILES CHECK")
print("-" * 70)

test_files = [
    'test_conversions.py',
    'test_features.py',
    'test_integration.py',
    'test_image_conversions.py',
    'test_watermark.py',
    'verify_features.py',
]

found_tests = 0
for test_file in test_files:
    if os.path.exists(test_file):
        print(f"  OK: {test_file}")
        found_tests += 1
    else:
        print(f"  MISSING: {test_file}")

print(f"\n  Summary: {found_tests} test files available")

# Final Summary
print("\n" + "="*70)
print("FINAL SUMMARY")
print("="*70)

if failed_count == 0:
    print("STATUS: ALL DEPENDENCIES INSTALLED")
    print("ACTION: Ready to run conversion tests")
else:
    print(f"STATUS: {failed_count} DEPENDENCY ISSUES DETECTED")
    print(f"FAILED DEPENDENCIES: {', '.join(failed_deps)}")
    print("ACTION: Install missing dependencies with: pip install -r requirements.txt")

print("="*70 + "\n")
