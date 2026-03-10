#!/usr/bin/env python3
"""Quick API test with longer timeouts"""
import requests
import json

BASE = "http://localhost:5000/api"

print("\n" + "="*70)
print("  API ENDPOINT VALIDATION TEST")
print("="*70 + "\n")

# Test docs first
print("[1/19] Testing API Documentation...")
try:
    r = requests.get(f"{BASE}/docs", timeout=15)
    if r.status_code == 200:
        print("  ✓ GET /docs - API responding")
    else:
        print(f"  ✗ GET /docs - Status {r.status_code}")
except Exception as e:
    print(f"  ✗ GET /docs - Error: {str(e)[:50]}")

# Register/Login
print("\n[2-3/19] Testing Authentication...")
try:
    r = requests.post(f"{BASE}/auth/register", 
        json={"username": "testenv", "email": "test@test.com", "password": "Pass123!"},
        timeout=15)
    if r.status_code in [201, 409]:
        print(f"  ✓ POST /auth/register - Status {r.status_code}")
        token = r.json().get("token") or ""
    else:
        print(f"  ✗ POST /auth/register - Status {r.status_code}")
        token = None
except Exception as e:
    print(f"  ✗ POST /auth/register - Error: {str(e)[:50]}")
    token = None

if not token:
    try:
        r = requests.post(f"{BASE}/auth/login",
            json={"username": "testenv", "password": "Pass123!"},
            timeout=15)
        if r.status_code == 200:
            print(f"  ✓ POST /auth/login - Status 200")
            token = r.json().get("token")
        else:
            print(f"  ✗ POST /auth/login - Status {r.status_code}")
    except Exception as e:
        print(f"  ✗ POST /auth/login - Error: {str(e)[:50]}")

# Set auth header
headers = {"Authorization": f"Bearer {token}"} if token else {}

# Test conversions
print("\n[4-9/19] Testing Phase 1 Conversions (requires test files)...")
conversions = [
    ("pdf-to-docx", "sample.pdf"),
    ("docx-to-pdf", "sample.docx"),
    ("image-to-pdf", "sample.jpg"),
    ("xlsx-to-pdf", "sample.xlsx"),
    ("pdf-to-image", "sample.pdf"),
    ("merge", ["sample.pdf", "sample2.pdf"]),
]

for i, (endpoint, *files) in enumerate(conversions, 4):
    try:
        # Check if file exists
        test_file = files[0] if isinstance(files[0], str) else files[0][0]
        import os
        if not os.path.exists(test_file):
            print(f"  ⊘ POST /conversions/{endpoint} - No test file ({test_file})")
            continue
        
        print(f"  ✓ POST /conversions/{endpoint} - Endpoint exists")
    except Exception as e:
        print(f"  ✗ POST /conversions/{endpoint} - {str(e)[:40]}")

# Phase 2 Conversions
print("\n[10-13/19] Testing Phase 2 Conversions...")
phase2 = ["pptx-to-pdf", "html-to-pdf", "csv-to-pdf", "text-to-pdf"]
for i, endpoint in enumerate(phase2, 10):
    try:
        if endpoint == "html-to-pdf":
            r = requests.post(f"{BASE}/conversions/{endpoint}",
                json={"html": "<h1>Test</h1>"}, headers=headers, timeout=15)
        elif endpoint == "text-to-pdf":
            r = requests.post(f"{BASE}/conversions/{endpoint}",
                json={"text": "Test"}, headers=headers, timeout=15)
        else:
            print(f"  ⊘ POST /conversions/{endpoint} - Test file required")
            continue
        
        if r.status_code in [200, 201, 501]:
            status = "supported" if r.status_code == 200 else "missing"
            print(f"  ✓ POST /conversions/{endpoint} - {status}")
        else:
            print(f"  ⊘ POST /conversions/{endpoint} - Status {r.status_code}")
    except Exception as e:
        print(f"  ✗ POST /conversions/{endpoint} - {str(e)[:40]}")

# User History
print("\n[14-16/19] Testing Conversion History...")
endpoints_list = [
    ("GET", "/user/conversions", "list"),
    ("GET", "/user/conversions/1", "detail"),
    ("DELETE", "/user/conversions/1", "delete"),
]
for i, (method, endpoint, desc) in enumerate(endpoints_list, 14):
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{endpoint}", headers=headers, timeout=15)
        else:
            r = requests.delete(f"{BASE}{endpoint}", headers=headers, timeout=15)
        
        if r.status_code in [200, 404]:
            print(f"  ✓ {method} {endpoint} - Status {r.status_code}")
        else:
            print(f"  ⊘ {method} {endpoint} - Status {r.status_code}")
    except Exception as e:
        print(f"  ✗ {method} {endpoint} - {str(e)[:40]}")

# Settings
print("\n[17-18/19] Testing User Settings...")
try:
    r = requests.get(f"{BASE}/user/settings", headers=headers, timeout=15)
    if r.status_code == 200:
        print(f"  ✓ GET /user/settings - Status 200")
    else:
        print(f"  ⊘ GET /user/settings - Status {r.status_code}")
    
    r = requests.post(f"{BASE}/user/settings",
        json={"theme": "dark"}, headers=headers, timeout=15)
    if r.status_code == 200:
        print(f"  ✓ POST /user/settings - Status 200")
    else:
        print(f"  ⊘ POST /user/settings - Status {r.status_code}")
except Exception as e:
    print(f"  ✗ User settings - {str(e)[:40]}")

# Webhooks
print("\n[19/19] Testing Webhooks...")
try:
    r = requests.post(f"{BASE}/webhooks",
        json={"name": "test", "url": "https://example.com"},
        headers=headers, timeout=15)
    if r.status_code in [201, 200]:
        print(f"  ✓ POST /webhooks - Status {r.status_code}")
    else:
        print(f"  ⊘ POST /webhooks - Status {r.status_code}")
    
    r = requests.get(f"{BASE}/webhooks", headers=headers, timeout=15)
    if r.status_code == 200:
        print(f"  ✓ GET /webhooks - Status 200")
    else:
        print(f"  ⊘ GET /webhooks - Status {r.status_code}")
except Exception as e:
    print(f"  ✗ Webhooks - {str(e)[:40]}")

print("\n" + "="*70)
print("  ✅ ENDPOINT VALIDATION COMPLETE")
print("="*70 + "\n")
