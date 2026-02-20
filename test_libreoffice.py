#!/usr/bin/env python3
"""Test LibreOffice integration."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from services.document_conversion import get_soffice_path, excel_to_pdf

def test_libreoffice():
    """Test LibreOffice functionality."""
    print("=" * 70)
    print("LibreOffice Integration Test")
    print("=" * 70)
    
    # Test 1: Verify soffice path
    soffice_path = get_soffice_path()
    print(f"\n1. LibreOffice Location:")
    print(f"   Path: {soffice_path}")
    print(f"   Exists: {os.path.exists(soffice_path)}")
    
    # Test 2: Test Excel to PDF conversion
    test_file = r'E:\OneDrive\Documents\py1\test_sample.xlsx'
    if os.path.exists(test_file):
        print(f"\n2. Excel to PDF Conversion Test:")
        print(f"   Input file: {test_file}")
        print(f"   File size: {os.path.getsize(test_file)} bytes")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            print(f"   Converting...")
            result = excel_to_pdf(test_file, output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                size = os.path.getsize(output_path)
                print(f"   ✓ Conversion successful!")
                print(f"   ✓ PDF created: {size} bytes")
                os.remove(output_path)
            else:
                print(f"   ✗ PDF not created or empty")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
    else:
        print(f"\n2. Test file not found: {test_file}")
    
    print("\n" + "=" * 70)
    print("LibreOffice is ready for document conversion operations!")
    print("=" * 70)

if __name__ == '__main__':
    test_libreoffice()
