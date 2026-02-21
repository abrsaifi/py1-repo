#!/usr/bin/env python3
"""Test the PDF conversion API"""

import requests
import json

# Test parameters
url = "http://localhost:5000/api/convert"
csv_file = "test_data.csv"

# Read the CSV file
with open(csv_file, 'rb') as f:
    files = {'files[]': f}
    
    # Test data with all new parameters
    data = {
        'tool_name': 'To PDF',
        'output_format': 'pdf',
        'quality': '85',
        'orientation': 'landscape',
        'paper_size': 'A4',
        'margin_top': '15',
        'margin_bottom': '15',
        'margin_left': '10',
        'margin_right': '10',
        'fit_mode': 'fit-page',
        'include_headers': 'true',
        'gridlines': 'true',
        'scale_factor': '80',
        'image_quality': '75',
        'page_numbers': 'true',
        'compression': 'high',
        'preserve_colors': 'true',
        'embed_fonts': 'true',
        'background': 'true'
    }
    
    print("Testing PDF conversion with enhanced parameters...")
    print(f"Parameters: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, files=files, data=data)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print(f"Output file: {result.get('output')}")
            print(f"File size: {result.get('file_size')} bytes")
            print(f"Preview: {result.get('preview_type')}")
            print("\n✅ Conversion successful with all new features!")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"Error: {response.text}")
