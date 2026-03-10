#!/usr/bin/env python
"""
End-to-end test of hybrid LibreOffice conversion.
Tests the /convert-to-pdf endpoint with the test client.
"""

import os
import sys
import tempfile
from pathlib import Path

# Configure hybrid mode
os.environ['LIBREOFFICE_PREFER_DAEMON'] = '1'
os.environ['LIBREOFFICE_DAEMON_HOST'] = 'localhost'
os.environ['LIBREOFFICE_DAEMON_PORT'] = '2002'

from server import app

def test_hybrid_conversion_endpoint():
    """Test the /convert-to-pdf endpoint with hybrid mode."""
    
    print("[TEST] Creating test CSV file...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use CSV which is supported
        test_file = Path(tmpdir) / 'test.csv'
        test_file.write_text('Name,Value\nTest,123\n')
        
        print(f"[OK] Test file created: {test_file}")
        
        # Test the endpoint with Flask test client
        with app.test_client() as client:
            print("\n[TEST] POST /convert-to-pdf")
            with open(test_file, 'rb') as f:
                response = client.post(
                    '/convert-to-pdf',
                    content_type='multipart/form-data',
                    data={'files': (f, 'test.csv')}
                )
            
            print(f"[RESPONSE] Status: {response.status_code}")
            print(f"[RESPONSE] Content-Type: {response.content_type}")
            
            if response.status_code == 200:
                if response.content_type and 'pdf' in response.content_type:
                    pdf_size = len(response.data)
                    print(f"[SUCCESS] PDF generated! Size: {pdf_size} bytes")
                    return True
                else:
                    print(f"[WARN] Response is {response.status_code} but not PDF")
                    data = response.get_data(as_text=True)
                    print(f"[DATA] {data[:200]}")
            elif response.status_code == 302:
                print(f"[INFO] Got redirect (302) - likely auth required")
                print(f"[LOCATION] {response.headers.get('Location')}")
            else:
                data = response.get_data(as_text=True)
                print(f"[ERROR] {data}")
                return False

def test_root_endpoint():
    """Test the root / endpoint."""
    print("[TEST] GET /")
    with app.test_client() as client:
        response = client.get('/')
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"[SUCCESS] Root endpoint returns HTML (size: {len(response.data)} bytes)")
            return True
        else:
            print(f"[ERROR] Unexpected status: {response.status_code}")
            return False

if __name__ == '__main__':
    print("=" * 70)
    print("HYBRID LIBREOFFICE E2E TEST")
    print("=" * 70)
    
    print("\n[CONFIG]")
    print(f"  LIBREOFFICE_PREFER_DAEMON={os.environ.get('LIBREOFFICE_PREFER_DAEMON')}")
    print(f"  LIBREOFFICE_DAEMON_HOST={os.environ.get('LIBREOFFICE_DAEMON_HOST')}")
    print(f"  LIBREOFFICE_DAEMON_PORT={os.environ.get('LIBREOFFICE_DAEMON_PORT')}")
    
    print("\n" + "=" * 70)
    success = True
    
    print("\nTest 1: Root Endpoint")
    print("-" * 70)
    if not test_root_endpoint():
        success = False
    
    print("\n\nTest 2: Conversion Endpoint (Hybrid Mode)")
    print("-" * 70)
    if not test_hybrid_conversion_endpoint():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
