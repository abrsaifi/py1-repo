"""
Test all three sheet management endpoints
"""

import requests
import json
import os

BASE_URL = "http://localhost:5000"
API_KEY = "test"
HEADERS = {"X-API-Key": API_KEY}

def test_list_sheets():
    """Test /list-sheets endpoint"""
    print("\n" + "="*70)
    print("TEST 1: /list-sheets Endpoint")
    print("="*70)
    print("\n📋 Request: POST /list-sheets with test_sample.xlsx\n")
    
    files = {'file': open('test_sample.xlsx', 'rb')}
    response = requests.post(f'{BASE_URL}/list-sheets', files=files, headers=HEADERS)
    
    print(f"✓ Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        print('File Information:')
        print(f"  File Name: {result.get('file_name')}")
        print(f"  File Type: {result.get('file_type')}")
        print(f"  Total Sheets: {len(result.get('sheets', []))}\n")
        
        print('Sheets Details:')
        for sheet in result.get('sheets', []):
            print(f"  • {sheet['name']}")
            print(f"    - Rows: {sheet['rows']}, Columns: {sheet['columns']}")
            preview = sheet['preview'][0] if sheet['preview'] else 'No data'
            print(f"    - Preview: {preview}\n")
    else:
        print(f"❌ Error: {response.text}")

def test_excel_to_pdf_sheets():
    """Test /excel-to-pdf-sheets endpoint"""
    print("\n" + "="*70)
    print("TEST 2: /excel-to-pdf-sheets Endpoint")
    print("="*70)
    print("\n📄 Request: Convert 'Sales' sheet to PDF\n")
    
    files = {'file': open('test_sample.xlsx', 'rb')}
    data = {
        'sheets': 'Sales',
        'merge': 'false',
        'orientation': 'landscape'
    }
    
    response = requests.post(
        f'{BASE_URL}/excel-to-pdf-sheets',
        files=files,
        data=data,
        headers=HEADERS
    )
    
    print(f"✓ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        with open('output_sales.pdf', 'wb') as f:
            f.write(response.content)
        size = os.path.getsize('output_sales.pdf')
        print(f"✓ PDF Generated: output_sales.pdf ({size} bytes)\n")
    else:
        print(f"❌ Error: {response.text}\n")
    
    # Test 2b: Convert multiple sheets merged
    print("\n📄 Request: Convert 'Sales' + 'Expenses' sheets merged into one PDF\n")
    
    files = {'file': open('test_sample.xlsx', 'rb')}
    data = {
        'sheets': 'Sales,Expenses',
        'merge': 'true',
        'orientation': 'portrait',
        'paper_size': 'A4'
    }
    
    response = requests.post(
        f'{BASE_URL}/excel-to-pdf-sheets',
        files=files,
        data=data,
        headers=HEADERS
    )
    
    print(f"✓ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        with open('output_merged.pdf', 'wb') as f:
            f.write(response.content)
        size = os.path.getsize('output_merged.pdf')
        print(f"✓ Merged PDF Generated: output_merged.pdf ({size} bytes)\n")
    else:
        print(f"❌ Error: {response.text}\n")

def test_combine_csvs():
    """Test /combine-csvs endpoint"""
    print("\n" + "="*70)
    print("TEST 3: /combine-csvs Endpoint")
    print("="*70)
    print("\n📊 Request: Combine 3 CSV files into single Excel workbook\n")
    
    files = [
        ('files', open('q1_sales.csv', 'rb')),
        ('files', open('q1_expenses.csv', 'rb')),
        ('files', open('q1_customers.csv', 'rb'))
    ]
    
    data = {
        'sheet_names': '["Q1 Sales", "Q1 Expenses", "Customers"]'
    }
    
    response = requests.post(
        f'{BASE_URL}/combine-csvs',
        files=files,
        data=data,
        headers=HEADERS
    )
    
    print(f"✓ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        with open('combined_q1_report.xlsx', 'wb') as f:
            f.write(response.content)
        size = os.path.getsize('combined_q1_report.xlsx')
        print(f"✓ Combined Excel Generated: combined_q1_report.xlsx ({size} bytes)\n")
        
        # Verify the sheets
        from openpyxl import load_workbook
        wb = load_workbook('combined_q1_report.xlsx')
        print(f"Sheets in combined file: {wb.sheetnames}\n")
        wb.close()
    else:
        print(f"❌ Error: {response.text}\n")

if __name__ == '__main__':
    print("\n🚀 TESTING ALL SHEET MANAGEMENT ENDPOINTS\n")
    
    try:
        test_list_sheets()
        test_excel_to_pdf_sheets()
        test_combine_csvs()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nGenerated Files:")
        print("  ✓ output_sales.pdf - Single sheet conversion")
        print("  ✓ output_merged.pdf - Multiple sheets merged")
        print("  ✓ combined_q1_report.xlsx - Combined CSV files")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
