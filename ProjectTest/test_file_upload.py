#!/usr/bin/env python3
"""
Test file upload handling for conversion endpoints.
"""

import sys
from pathlib import Path

# Add workspace to path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def test_file_upload_routes():
    """Verify file upload routes have correct field names."""
    import server
    from io import BytesIO
    from werkzeug.datastructures import FileStorage
    
    print("=" * 70)
    print("TESTING FILE UPLOAD FIELD NAMES")
    print("=" * 70)
    print()
    
    app = server.app
    test_results = []
    
    # Test 1: /convert endpoint with 'files' field
    with app.test_client() as client:
        print("Test 1: /convert endpoint")
        try:
            # Create a fake PDF file
            pdf_content = b"%PDF-1.4\n%fake pdf content"
            data = {'files': (BytesIO(pdf_content), 'test.pdf')}
            response = client.post('/convert', data=data, content_type='multipart/form-data')
            
            # Should return either success or proper error (not "No files uploaded" for wrong field name)
            if response.status_code in [200, 302] or 'No file' not in response.data.decode():
                print("  ✓ File upload field 'files' is correctly recognized")
                test_results.append(True)
            else:
                print("  ✗ File upload field issue detected")
                test_results.append(False)
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:60]}")
            test_results.append(False)
    
    # Test 2: /convert-to-pdf endpoint with 'files' field
    with app.test_client() as client:
        print("Test 2: /convert-to-pdf endpoint")
        try:
            # Create a fake image file
            img_content = b"fake image content"
            data = {'files': (BytesIO(img_content), 'test.jpg')}
            response = client.post('/convert-to-pdf', data=data, content_type='multipart/form-data')
            
            if response.status_code in [200, 302] or 'No file' not in response.data.decode():
                print("  ✓ File upload field 'files' is correctly recognized")
                test_results.append(True)
            else:
                print("  ✗ File upload field issue detected")
                test_results.append(False)
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:60]}")
            test_results.append(False)
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if all(test_results):
        print("✓ All file upload tests passed!")
        print()
        print("The file upload issues have been fixed:")
        print("  • /convert now accepts 'files' field (was 'pdf_file')")
        print("  • /convert-to-pdf now accepts 'files' field (was 'file')")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(test_file_upload_routes())
