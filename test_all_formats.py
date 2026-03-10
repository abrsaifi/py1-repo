#!/usr/bin/env python3
"""Test To PDF conversion with multiple file formats"""

import sys
sys.path.insert(0, '/c/Users/dell/OneDrive/Documents/py1')

import requests
from PIL import Image
import os

print("=" * 70)
print("MULTI-FORMAT PDF CONVERSION TEST")
print("=" * 70)

# Test data
test_formats = {
    'CSV': {'file': 'test_data.csv', 'expected': True},
    'EXCEL': {'file': 'q1_customers.csv', 'expected': True},  # CSV file
    'DOCX': {'file': 'test_document.docx', 'expected': True},
}

# Create a test image
image_path = "test_image.png"
img = Image.new('RGB', (800, 600), color='blue')
img.save(image_path)
print(f"\n✓ Created test image: {image_path}")

test_formats['IMAGE'] = {'file': image_path, 'expected': True}

# Common parameters for all formats
params = {
    'tool_name': 'To PDF',
    'orientation': 'landscape',
    'paper_size': 'A4',
    'margin_top': '12',
    'margin_bottom': '12',
    'margin_left': '15',
    'margin_right': '15',
    'scale_factor': '85',
    'page_numbers': 'true',
    'compression': 'high',
    'preserve_colors': 'true',
    'embed_fonts': 'true',
    'background': 'true'
}

results = {}

# Test each format
for format_name, test_info in test_formats.items():
    file_path = test_info['file']
    
    if not os.path.exists(file_path):
        print(f"\n⚠ {format_name}: File not found ({file_path})")
        results[format_name] = 'SKIPPED'
        continue
    
    try:
        print(f"\n{'=' * 70}")
        print(f"Testing {format_name}: {file_path}")
        print(f"Parameters: landscape, A4, margins=12/12/15/15mm, scale=85%, page#s, compression=high")
        
        with open(file_path, 'rb') as f:
            response = requests.post('http://localhost:5000/api/convert',
                files={'files[]': f},
                data=params,
                timeout=30
            )
        
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            if result.get('files') and len(result['files']) > 0:
                pdf_info = result['files'][0]
                print(f"✅ SUCCESS - {format_name} conversion")
                print(f"   PDF: {pdf_info['name']}")
                print(f"   Size: {pdf_info['size']} bytes")
                results[format_name] = 'SUCCESS'
            else:
                print(f"❌ FAILED - {format_name}: No output files")
                results[format_name] = 'FAILED'
        else:
            print(f"❌ FAILED - {format_name}: {result.get('error', 'Unknown error')}")
            results[format_name] = 'FAILED'
    
    except Exception as e:
        print(f"❌ ERROR - {format_name}: {str(e)}")
        results[format_name] = 'ERROR'

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
for format_name, status in results.items():
    status_icon = '✅' if status == 'SUCCESS' else '❌' if status in ('FAILED', 'ERROR') else '⚠ '
    print(f"{status_icon} {format_name:12} : {status}")

success_count = sum(1 for s in results.values() if s == 'SUCCESS')
total_count = len([s for s in results.values() if s != 'SKIPPED'])
print(f"\nResult: {success_count}/{total_count} formats successful")

if success_count == total_count:
    print("\n🎉 All formats working with advanced PDF parameters!")
else:
    print(f"\n⚠️  Some formats need attention")
