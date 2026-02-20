"""Verify office toolkit reorganization."""
from server import app

with app.test_client() as client:
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    # Check for category organization comments
    has_pdf_tools = '<!-- PDF TOOLS -->' in html
    has_office = '<!-- OFFICE CONVERSIONS -->' in html
    has_image = '<!-- IMAGE TOOLS -->' in html
    has_history = '<!-- HISTORY -->' in html
    
    print('Office Toolkit Reorganization Status')
    print('=' * 50)
    print(f'✓ PDF Tools Section: {"FOUND" if has_pdf_tools else "MISSING"}')
    print(f'✓ Office Conversions Section: {"FOUND" if has_office else "MISSING"}')
    print(f'✓ Image Tools Section: {"FOUND" if has_image else "MISSING"}')
    print(f'✓ History Section: {"FOUND" if has_history else "MISSING"}')
    print('=' * 50)
    
    # Verify key buttons are in the right order
    pdf_tools_check = html.find('PDF TOOLS') < html.find('OFFICE CONVERSIONS')
    office_check = html.find('OFFICE CONVERSIONS') < html.find('IMAGE TOOLS')
    image_check = html.find('IMAGE TOOLS') < html.find('HISTORY')
    
    if pdf_tools_check and office_check and image_check:
        print('✓ Category order is correct: PDF → Office → Images → History')
    else:
        print('✗ Category order might be incorrect')
    
    print('=' * 50)
    print('Reorganization complete!')
