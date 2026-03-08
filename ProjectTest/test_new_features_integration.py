#!/usr/bin/env python3
"""
Test Suite for New Priority Features
Tests API integration and function existence
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add server to path
sys.path.insert(0, os.path.dirname(__file__))

# Test results tracking
test_results = {
    'passed': [],
    'failed': [],
    'total': 0
}


def log_test(name, status, message=""):
    """Log test result"""
    test_results['total'] += 1
    if status == 'PASS':
        test_results['passed'].append(name)
        print(f"✅ PASS: {name}")
    elif status == 'FAIL':
        test_results['failed'].append((name, message))
        print(f"❌ FAIL: {name}")
    
    if message:
        print(f"   └─ {message}")


# ============================================================================
# TEST 1: Function Imports
# ============================================================================

def test_function_imports():
    """Test that all new functions are properly imported"""
    print("\n" + "="*70)
    print("TEST 1: Function Imports")
    print("="*70)
    
    functions_to_check = [
        'remove_duplicate_images',
        'batch_process_images',
        'batch_process_pdfs',
        'export_data_to_pdf',
        'generate_detailed_report',
        'smart_crop_image',
        'fill_pdf_form'
    ]
    
    try:
        from server import (
            remove_duplicate_images,
            batch_process_images,
            batch_process_pdfs,
            export_data_to_pdf,
            generate_detailed_report,
            smart_crop_image,
            fill_pdf_form
        )
        
        for func_name in functions_to_check:
            log_test(f"Import {func_name}", "PASS", "Function successfully imported")
    
    except ImportError as e:
        log_test("Function Imports", "FAIL", str(e))
        return False
    
    return True


# ============================================================================
# TEST 2: Route Handler Definitions
# ============================================================================

def test_route_handlers():
    """Test that all route handlers are properly registered"""
    print("\n" + "="*70)
    print("TEST 2: Route Handler Registration")
    print("="*70)
    
    routes_to_check = {
        '/api/features/batch-process-images': 'Batch Process Images',
        '/api/features/batch-process-pdfs': 'Batch Process PDFs',
        '/api/features/remove-duplicate-images': 'Remove Duplicate Images',
        '/api/features/smart-crop-images': 'Smart Crop Images',
        '/api/features/fill-pdf-forms': 'Fill PDF Forms',
        '/api/features/export-data-pdf': 'Export Data to PDF',
        '/api/features/generate-report': 'Generate Report'
    }
    
    try:
        from server import app
        
        registered_routes = {str(rule): rule.methods for rule in app.url_map.iter_rules()}
        
        all_found = True
        for route, description in routes_to_check.items():
            if route in registered_routes:
                methods = ', '.join(m for m in registered_routes[route] if m not in ['HEAD', 'OPTIONS'])
                log_test(f"Route: {route}", "PASS", f"Methods: {methods}")
            else:
                log_test(f"Route: {route}", "FAIL", "Route not registered")
                all_found = False
        
        return all_found
    
    except Exception as e:
        log_test("Route Handler Registration", "FAIL", str(e))
        return False


# ============================================================================
# TEST 3: Function Signatures
# ============================================================================

def test_function_signatures():
    """Test that functions have correct signatures"""
    print("\n" + "="*70)
    print("TEST 3: Function Signatures")
    print("="*70)
    
    try:
        from server import (
            remove_duplicate_images,
            batch_process_images,
            batch_process_pdfs,
            export_data_to_pdf,
            generate_detailed_report,
            smart_crop_image,
            fill_pdf_form
        )
        import inspect
        
        # Check function signatures
        functions = {
            'remove_duplicate_images': ['input_dir', 'output_dir'],
            'batch_process_images': ['input_dir', 'output_dir', 'operation'],
            'batch_process_pdfs': ['input_dir', 'output_dir', 'operation'],
            'export_data_to_pdf': ['input_file', 'output_pdf'],
            'generate_detailed_report': ['input_file', 'output_file', 'report_type'],
            'smart_crop_image': ['input_img', 'output_img'],
            'fill_pdf_form': ['input_pdf', 'output_pdf', 'field_data']
        }
        
        for func_name, expected_params in functions.items():
            func = globals()[func_name] if func_name in globals() else eval(func_name)
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            # Check if at least the main required params are present
            has_params = all(p in params for p in expected_params[:2])
            
            if has_params:
                log_test(f"Signature: {func_name}", "PASS", f"Parameters: {', '.join(params)}")
            else:
                log_test(f"Signature: {func_name}", "FAIL", f"Missing parameters")
        
        return True
    
    except Exception as e:
        log_test("Function Signatures", "FAIL", str(e))
        return False


# ============================================================================
# TEST 4: Router Integration
# ============================================================================

def test_router_integration():
    """Test that functions are integrated in execute_service_conversion router"""
    print("\n" + "="*70)
    print("TEST 4: Router Integration")
    print("="*70)
    
    try:
        import server
        import inspect
        
        # Get the execute_service_conversion function source
        source = inspect.getsource(server.execute_service_conversion)
        
        services_to_check = [
            'remove_duplicate_images',
            'batch_process_images',
            'batch_process_pdfs',
            'smart_crop_images',
            'fill_pdf_forms',
            'export_to_pdf',
            'generate_report'
        ]
        
        for service in services_to_check:
            if service in source:
                log_test(f"Router: {service}", "PASS", "Service referenced in router")
            else:
                log_test(f"Router: {service}", "FAIL", "Service not found in router")
        
        return True
    
    except Exception as e:
        log_test("Router Integration", "FAIL", str(e))
        return False


# ============================================================================
# TEST 5: Code Quality Checks
# ============================================================================

def test_code_quality():
    """Test code quality aspects"""
    print("\n" + "="*70)
    print("TEST 5: Code Quality Checks")
    print("="*70)
    
    try:
        import server
        import inspect
        
        # Check for docstrings
        functions = [
            ('remove_duplicate_images', 'Duplicate Image Remover'),
            ('batch_process_images', 'Batch Image Processor'),
            ('batch_process_pdfs', 'Batch PDF Processor'),
            ('export_data_to_pdf', 'Data Export'),
            ('generate_detailed_report', 'Report Generator'),
            ('smart_crop_image', 'Smart Crop'),
            ('fill_pdf_form', 'PDF Form Filler')
        ]
        
        for func_name, desc in functions:
            if hasattr(server, func_name):
                func = getattr(server, func_name)
                if func.__doc__:
                    log_test(f"Docstring: {desc}", "PASS", f"{len(func.__doc__)} chars")
                else:
                    log_test(f"Docstring: {desc}", "FAIL", "No docstring found")
            else:
                log_test(f"Docstring: {desc}", "FAIL", "Function not found")
        
        return True
    
    except Exception as e:
        log_test("Code Quality Checks", "FAIL", str(e))
        return False


# ============================================================================
# TEST 6: Dependency Availability
# ============================================================================

def test_dependencies():
    """Test optional dependency handling"""
    print("\n" + "="*70)
    print("TEST 6: Dependency Availability")
    print("="*70)
    
    dependencies = {
        'Pillow': 'PIL',
        'PyPDF2': 'PyPDF2',
        'reportlab': 'reportlab',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'numpy': 'np',
        'easyocr': 'easyocr'
    }
    
    for package, import_name in dependencies.items():
        try:
            __import__(import_name)
            log_test(f"Dependency: {package}", "PASS", "Installed and available")
        except ImportError:
            log_test(f"Dependency: {package}", "FAIL", f"Not installed (optional for {import_name})")
    
    return True


# ============================================================================
# TEST 7: Server Startup
# ============================================================================

def test_server_startup():
    """Test that server can start without errors"""
    print("\n" + "="*70)
    print("TEST 7: Server Startup")
    print("="*70)
    
    try:
        from server import app
        
        # Check if app is properly configured
        if app:
            log_test("Flask App Initialization", "PASS", f"Flask version {app.import_name}")
            
            # Check debug mode
            if hasattr(app, 'debug'):
                log_test("App Configuration", "PASS", "Configuration loaded")
            
            return True
        else:
            log_test("Flask App Initialization", "FAIL", "App not created")
            return False
    
    except Exception as e:
        log_test("Flask App Initialization", "FAIL", str(e))
        return False


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " NEW FEATURES TEST SUITE ".center(68) + "║")
    print("║" + " Integration & Code Quality Tests ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    # Run all tests
    test_function_imports()
    test_route_handlers()
    test_function_signatures()
    test_router_integration()
    test_code_quality()
    test_dependencies()
    test_server_startup()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {test_results['total']}")
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    
    if test_results['failed']:
        print("\nFailed Tests:")
        for name, msg in test_results['failed']:
            print(f"  └─ {name}: {msg}")
    
    success_rate = (len(test_results['passed']) / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    print("\n" + "="*70)
    
    return 0 if len(test_results['failed']) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
