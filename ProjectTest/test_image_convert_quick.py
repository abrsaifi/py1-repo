#!/usr/bin/env python
"""Quick test of image conversion to diagnose the "no files converted" issue."""

import os
import tempfile
from PIL import Image
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(__file__))

from server import convert_image_format, execute_service_conversion

def test_image_conversion():
    """Test basic image conversion."""
    print("Testing image conversion...")
    
    # Create a test image
    temp_dir = tempfile.mkdtemp()
    test_input = os.path.join(temp_dir, 'test.png')
    test_output = os.path.join(temp_dir, 'test_output.jpg')
    
    # Create a simple PNG
    img = Image.new('RGB', (100, 100), color='red')
    img.save(test_input)
    print(f"✓ Created test image: {test_input}")
    
    # Test 1: Direct function
    print("\nTest 1: Direct convert_image_format()")
    result = convert_image_format(test_input, test_output, 'jpg', quality=85)
    if result and os.path.exists(test_output):
        print(f"✓ Conversion successful: {test_output}")
        print(f"  File size: {os.path.getsize(test_output)} bytes")
    else:
        print(f"✗ Conversion failed")
        return False
    
    # Test 2: Via execute_service_conversion
    test_output2 = os.path.join(temp_dir, 'test_output2.jpg')
    print("\nTest 2: execute_service_conversion('Image Convert')")
    result2 = execute_service_conversion('Image Convert', test_input, test_output2, 
                                        output_format='jpg', quality=85)
    if result2 and os.path.exists(test_output2):
        print(f"✓ Conversion successful: {test_output2}")
        print(f"  File size: {os.path.getsize(test_output2)} bytes")
    else:
        print(f"✗ Conversion failed")
        return False
    
    # Test 3: Via execute_service_conversion with different tool name
    test_output3 = os.path.join(temp_dir, 'test_output3.png')
    print("\nTest 3: execute_service_conversion('Convert Images')")
    result3 = execute_service_conversion('Convert Images', test_input, test_output3, 
                                        output_format='png', quality=85)
    if result3 and os.path.exists(test_output3):
        print(f"✓ Conversion successful: {test_output3}")
        print(f"  File size: {os.path.getsize(test_output3)} bytes")
    else:
        print(f"✗ Conversion failed")
        return False
    
    print("\n✓ All tests passed!")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    return True

if __name__ == '__main__':
    success = test_image_conversion()
    sys.exit(0 if success else 1)
