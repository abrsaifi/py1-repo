#!/usr/bin/env python
"""Test script for the 5 new features"""
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import tempfile
import json

app = create_app()

print("=" * 70)
print("TESTING NEW FEATURES - 1 BY 1")
print("=" * 70)

# TEST 1: Duplicate Remover
print("\n" + "=" * 70)
print("TEST 1: Duplicate Remover")
print("=" * 70)

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("Name,Email,Age\n")
    f.write("John Doe,john@example.com,30\n")
    f.write("Jane Smith,jane@example.com,25\n")
    f.write("John Doe,john@example.com,30\n")  # Duplicate
    f.write("Bob Johnson,bob@example.com,35\n")
    f.write("Jane Smith,jane@example.com,25\n")  # Duplicate
    dup_file = f.name

try:
    with app.test_client() as client:
        with open(dup_file, 'rb') as f:
            response = client.post('/api/data/duplicate-remover', data={'file': (f, 'test.csv')})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ SUCCESS: Duplicate remover endpoint works!")
            print(f"  Response size: {len(response.data)} bytes")
            print(f"  Content-Type: {response.content_type}")
        else:
            print(f"✗ FAILED")
            try:
                error = response.get_json()
                print(f"  Error: {error}")
            except:
                print(f"  Response: {response.data[:200]}")
finally:
    os.unlink(dup_file)

# TEST 2: Data Validator
print("\n" + "=" * 70)
print("TEST 2: Data Validator")
print("=" * 70)

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("Name,Score,Status\n")
    f.write("Alice,95,Pass\n")
    f.write("Bob,87,Pass\n")
    f.write("Charlie,,Pending\n")  # Missing value
    f.write("Diana,92,Pass\n")
    validator_file = f.name

try:
    with app.test_client() as client:
        with open(validator_file, 'rb') as f:
            response = client.post('/api/data/validate', data={'file': (f, 'test.csv')})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                report = data.get('report', {})
                print("✓ SUCCESS: Data validator endpoint works!")
                print(f"  Total rows: {report.get('total_rows')}")
                print(f"  Total columns: {report.get('total_columns')}")
                print(f"  Quality score: {report.get('quality_score')}%")
                print(f"  Duplicate rows: {report.get('duplicate_rows')}")
            else:
                print(f"✗ FAILED: {data.get('error')}")
        else:
            print(f"✗ FAILED: Status {response.status_code}")
finally:
    os.unlink(validator_file)

# TEST 3: PDF Export
print("\n" + "=" * 70)
print("TEST 3: PDF Export Enhancements")
print("=" * 70)

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("Product,Price,Quantity\n")
    f.write("Laptop,1200,5\n")
    f.write("Mouse,25,50\n")
    f.write("Keyboard,75,30\n")
    export_file = f.name

try:
    with app.test_client() as client:
        with open(export_file, 'rb') as f:
            response = client.post('/api/data/export-pdf', data={
                'file': (f, 'test.csv'),
                'format': 'table'
            })
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ SUCCESS: PDF export endpoint works!")
            print(f"  PDF file size: {len(response.data)} bytes")
            print(f"  Content-Type: {response.content_type}")
        else:
            print(f"✗ FAILED: Status {response.status_code}")
            try:
                error = response.get_json()
                print(f"  Error: {error.get('error')}")
            except:
                print(f"  Response: {response.data[:200]}")
finally:
    os.unlink(export_file)

# TEST 4: Basic Reporting
print("\n" + "=" * 70)
print("TEST 4: Basic Reporting")
print("=" * 70)

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write("Month,Sales,Expenses\n")
    f.write("January,50000,30000\n")
    f.write("February,55000,32000\n")
    f.write("March,60000,35000\n")
    f.write("April,58000,33000\n")
    report_file = f.name

try:
    with app.test_client() as client:
        with open(report_file, 'rb') as f:
            response = client.post('/api/data/reporting', data={'file': (f, 'test.csv')})
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                report = data.get('report', {})
                print("✓ SUCCESS: Reporting endpoint works!")
                print(f"  Total rows: {report.get('total_rows')}")
                print(f"  Total columns: {report.get('total_columns')}")
                stats = report.get('summary_statistics', {})
                for col, values in stats.items():
                    print(f"  {col}: Mean={values.get('mean')}, Min={values.get('min')}, Max={values.get('max')}")
            else:
                print(f"✗ FAILED: {data.get('error')}")
        else:
            print(f"✗ FAILED: Status {response.status_code}")
finally:
    os.unlink(report_file)

# TEST 5: Database Integration
print("\n" + "=" * 70)
print("TEST 5: Database Integration")
print("=" * 70)

with app.test_client() as client:
    response = client.post('/api/data/database-connect',
        json={
            'db_type': 'postgresql',
            'host': 'localhost',
            'port': '5432',
            'database': 'testdb',
            'username': 'admin'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        if data.get('success'):
            print("✓ SUCCESS: Database integration endpoint works!")
            conn = data.get('connection', {})
            print(f"  Database Type: {conn.get('db_type')}")
            print(f"  Host: {conn.get('host')}:{conn.get('port')}")
            print(f"  Database: {conn.get('database')}")
            print(f"  Status: {conn.get('status')}")
        else:
            print(f"✗ FAILED: {data.get('error')}")
    else:
        print(f"✗ FAILED: Status {response.status_code}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
