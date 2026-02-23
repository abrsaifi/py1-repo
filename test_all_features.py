#!/usr/bin/env python3
"""Test all 5 core PDF conversion features"""

import sys
sys.path.insert(0, '/c/Users/dell/OneDrive/Documents/py1')

import requests
from PIL import Image
from docx import Document
import os

print("=" * 80)
print("COMPREHENSIVE PDF CONVERSION FEATURE TEST")
print("=" * 80)

# Ensure server is running
try:
    response = requests.get('http://localhost:5000/', timeout=5)
    print("✅ Server is running at http://localhost:5000\n")
except:
    print("❌ Server is not running. Please start it first!")
    sys.exit(1)

# Create test files
print("Setting up test files...")

# 1. JPG Image
jpg_path = "test_image.jpg"
img = Image.new('RGB', (800, 600), color=(100, 150, 200))
img.save(jpg_path, 'JPEG')
print(f"  ✓ Created {jpg_path}")

# 2. Word Document (DOCX)
docx_path = "test_word.docx"
doc = Document()
doc.add_heading('Sample Word Document', 0)
doc.add_paragraph('This is a test Word document for PDF conversion.')
doc.add_paragraph('It contains multiple paragraphs and formatting.')
doc.save(docx_path)
print(f"  ✓ Created {docx_path}")

# 3. PowerPoint (if available, otherwise skip)
try:
    from pptx import Presentation
    pptx_path = "test_powerpoint.pptx"
    prs = Presentation()
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    title_box = slide.shapes.title
    body_shape = slide.placeholders[1]
    title_box.text = "Sample Presentation"
    body_shape.text = "This is a test presentation for PDF conversion."
    prs.save(pptx_path)
    print(f"  ✓ Created {pptx_path}")
    has_pptx = True
except:
    print(f"  ⚠ PowerPoint library not available, skipping PPTX")
    has_pptx = False

# 4. Excel (using existing file or create new)
xlsx_path = "test_excel.xlsx"
try:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws['A1'] = 'Name'
    ws['B1'] = 'Value'
    ws['A2'] = 'Item 1'
    ws['B2'] = 100
    ws['A3'] = 'Item 2'
    ws['B3'] = 200
    wb.save(xlsx_path)
    print(f"  ✓ Created {xlsx_path}")
except:
    print(f"  ⚠ Could not create Excel file")
    xlsx_path = None

# 5. HTML
html_path = "test_page.html"
with open(html_path, 'w') as f:
    f.write('''<html>
<head><title>Test Page</title></head>
<body>
<h1>Sample HTML Document</h1>
<p>This is a test HTML page for PDF conversion.</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
<li>Item 3</li>
</ul>
</body>
</html>''')
print(f"  ✓ Created {html_path}")

print("\n" + "=" * 80)
print("TESTING CONVERSIONS")
print("=" * 80)

tests = [
    ("JPG to PDF", jpg_path, "To PDF"),
    ("Word to PDF", docx_path, "To PDF"),
    ("Excel to PDF", xlsx_path, "To PDF") if xlsx_path else None,
    ("PowerPoint to PDF", pptx_path, "To PDF") if has_pptx else None,
    ("HTML to PDF", html_path, "To PDF"),
]

# Remove None entries
tests = [t for t in tests if t is not None]

results = {}

for test_name, file_path, tool_name in tests:
    if not os.path.exists(file_path):
        print(f"\n❌ {test_name}: File not found ({file_path})")
        results[test_name] = "FILE_NOT_FOUND"
        continue
    
    try:
        print(f"\n{'─' * 80}")
        print(f"Testing: {test_name}")
        print(f"Tool: {tool_name}")
        print(f"Input: {file_path}")
        
        with open(file_path, 'rb') as f:
            response = requests.post('http://localhost:5000/api/convert',
                files={'files[]': f},
                data={
                    'tool_name': tool_name,
                    'output_format': 'pdf',
                    'quality': '85'
                },
                timeout=30
            )
        
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            if result.get('files') and len(result['files']) > 0:
                pdf_info = result['files'][0]
                print(f"✅ SUCCESS")
                print(f"   PDF: {pdf_info['name']}")
                print(f"   Size: {pdf_info['size']:,} bytes")
                print(f"   Download: {pdf_info.get('download_url', 'N/A')}")
                results[test_name] = "SUCCESS"
            else:
                print(f"❌ FAILED: No output files")
                results[test_name] = "NO_OUTPUT"
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ FAILED: {error}")
            print(f"   Response: {result}")
            results[test_name] = "FAILED"
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results[test_name] = "ERROR"

# Summary
print(f"\n{'=' * 80}")
print("TEST SUMMARY")
print(f"{'=' * 80}")

success_count = 0
for test_name, status in results.items():
    status_icon = '✅' if status == 'SUCCESS' else '❌'
    print(f"{status_icon} {test_name:30} : {status}")
    if status == 'SUCCESS':
        success_count += 1

total = len(results)
print(f"\n{'─' * 80}")
print(f"Result: {success_count}/{total} conversions successful")

if success_count == total:
    print("\n🎉 ALL FEATURES WORKING PERFECTLY!")
elif success_count >= total * 0.8:
    print(f"\n✅ Most features working ({success_count}/{total})")
else:
    print(f"\n⚠️  Some features need attention ({success_count}/{total})")

# Cleanup
print(f"\n{'─' * 80}")
print("Cleaning up test files...")
for _, file_path, _ in tests:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            # Don't print cleanup messages, keep output clean
        except:
            pass

print("Done!")
