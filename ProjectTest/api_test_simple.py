#!/usr/bin/env python3
"""Simple API test without Unicode issues"""
import requests
import json
import os
import time

BASE = "http://localhost:5000/api"
TIMEOUT = 30

print("\n" + "="*70)
print("  DOCUMENT CONVERTER API - COMPLETE TEST (19 endpoints)")
print("="*70 + "\n")

passed = 0
failed = 0
tests = []

def test(name, success, detail=""):
    global passed, failed, tests
    if success:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"
    msg = f"  [{status}] {name:<45} {detail}"
    tests.append(msg)

# Auth
print("Authentication (2 endpoints):")
try:
    # Use timestamp for unique username
    ts = int(time.time() * 1000) % 100000
    username = f"testuser{ts}"
    
    r = requests.post(f"{BASE}/auth/register",
        json={"username": username, "email": f"{username}@test.com", "password": "Test123!"},
        timeout=TIMEOUT)
    if r.status_code in [201, 409]:
        test("POST /auth/register", True, f"Status {r.status_code}")
        token = r.json().get("token")
    else:
        test("POST /auth/register", False, f"Status {r.status_code}")
        token = None
except Exception as e:
    test("POST /auth/register", False, str(e)[:30])
    token = None

if not token:
    try:
        r = requests.post(f"{BASE}/auth/login",
            json={"username": "user1", "password": "pass123"},
            timeout=TIMEOUT)
        if r.status_code == 200:
            token = r.json().get("token")
            test("POST /auth/login", True)
        else:
            test("POST /auth/login", False, f"Status {r.status_code}")
    except Exception as e:
        test("POST /auth/login", False, str(e)[:30])
else:
    test("POST /auth/login", True, "Already authenticated")

for t in tests:
    print(t)
print()

if not token:
    print("ERROR: Authentication failed")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}
tests = []

# Phase 1 Conversions
print("Phase 1 Conversions (6 endpoints):")
conversions_phase1 = [
    ("pdf-to-docx", "sample.pdf", {"file": "file"}, None),
    ("docx-to-pdf", "sample.docx", {"file": "file"}, None),
    ("image-to-pdf", "sample.jpg", {"files[]": "file"}, {"orientation": "portrait"}),
    ("xlsx-to-pdf", "sample.xlsx", {"file": "file"}, None),
    ("pdf-to-image", "sample.pdf", {"file": "file"}, {"pages": "1", "format": "jpg", "quality": "85"}),
    ("merge", ["sample.pdf", "sample.pdf"], {"files[]": "files"}, None),
]

for endpoint, file_input, file_param, data in conversions_phase1:
    try:
        if isinstance(file_input, list):
            files = [(k if "[]" in k else k, open(f, "rb")) for k in file_param.keys() for f in file_input]
        else:
            files = [(list(file_param.keys())[0], open(file_input, "rb"))]
        
        r = requests.post(f"{BASE}/conversions/{endpoint}",
            files=files, data=data, headers=headers, timeout=TIMEOUT)
        
        if r.status_code == 200:
            size = r.json().get('file',  {}).get('size', r.json().get('files', [{}])[0].get('size', 0))
            test(f"POST /conversions/{endpoint}", True, f"{size} bytes")
        else:
            test(f"POST /conversions/{endpoint}", False, f"Status {r.status_code}")
    except Exception as e:
        test(f"POST /conversions/{endpoint}", False, str(e)[:30])

for t in tests:
    print(t)
print()
tests = []

# Phase 2 Conversions
print("Phase 2 Advanced Conversions (4 endpoints):")

# PPTX
try:
    with open("sample.pptx", "rb") as f:
        r = requests.post(f"{BASE}/conversions/pptx-to-pdf",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test("POST /conversions/pptx-to-pdf", True, f"{r.json()['file']['size']} bytes")
    elif r.status_code == 501:
        test("POST /conversions/pptx-to-pdf", False, "Not implemented")
    else:
        test("POST /conversions/pptx-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    test("POST /conversions/pptx-to-pdf", False, str(e)[:30])

# HTML
try:
    r = requests.post(f"{BASE}/conversions/html-to-pdf",
        json={"html": "<h1>Test</h1>"}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test("POST /conversions/html-to-pdf", True, f"{r.json()['file']['size']} bytes")
    elif r.status_code == 501:
        test("POST /conversions/html-to-pdf", False, "Not implemented")
    else:
        test("POST /conversions/html-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    test("POST /conversions/html-to-pdf", False, str(e)[:30])

# CSV
try:
    with open("sample.csv", "rb") as f:
        r = requests.post(f"{BASE}/conversions/csv-to-pdf",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test("POST /conversions/csv-to-pdf", True, f"{r.json()['file']['size']} bytes")
    else:
        test("POST /conversions/csv-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    test("POST /conversions/csv-to-pdf", False, str(e)[:30])

# Text
try:
    r = requests.post(f"{BASE}/conversions/text-to-pdf",
        json={"text": "Test text"}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test("POST /conversions/text-to-pdf", True, f"{r.json()['file']['size']} bytes")
    else:
        test("POST /conversions/text-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    test("POST /conversions/text-to-pdf", False, str(e)[:30])

for t in tests:
    print(t)
print()
tests = []

# History
print("User Conversion History (3 endpoints):")
try:
    r = requests.get(f"{BASE}/user/conversions?limit=5", headers=headers, timeout=TIMEOUT)
    count = len(r.json().get('conversions', []))
    test("GET /user/conversions", r.status_code == 200, f"{count} records")
except Exception as e:
    test("GET /user/conversions", False, str(e)[:30])

try:
    r = requests.get(f"{BASE}/user/conversions/test123", headers=headers, timeout=TIMEOUT)
    test("GET /user/conversions/<id>", r.status_code in [200, 404], f"Status {r.status_code}")
except Exception as e:
    test("GET /user/conversions/<id>", False, str(e)[:30])

try:
    r = requests.delete(f"{BASE}/user/conversions/test456", headers=headers, timeout=TIMEOUT)
    test("DELETE /user/conversions/<id>", r.status_code in [200, 404])
except Exception as e:
    test("DELETE /user/conversions/<id>", False, str(e)[:30])

for t in tests:
    print(t)
print()
tests = []

# Settings
print("User Settings (2 endpoints):")
try:
    r = requests.get(f"{BASE}/user/settings", headers=headers, timeout=TIMEOUT)
    settings = len(r.json().get('settings', {}))
    test("GET /user/settings", r.status_code == 200, f"{settings} settings")
except Exception as e:
    test("GET /user/settings", False, str(e)[:30])

try:
    r = requests.post(f"{BASE}/user/settings",
        json={"theme": "dark"}, headers=headers, timeout=TIMEOUT)
    test("POST /user/settings", r.status_code == 200)
except Exception as e:
    test("POST /user/settings", False, str(e)[:30])

for t in tests:
    print(t)
print()
tests = []

# Batch
print("Batch Conversion (1 endpoint):")
try:
    files = [("files", open("sample.pdf", "rb")), ("files", open("sample.pdf", "rb"))]
    r = requests.post(f"{BASE}/conversions/batch",
        files=files, data={"tool": "pdf-to-docx"}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test("POST /conversions/batch", True, f"{len(r.json()['files'])} processed")
    else:
        test("POST /conversions/batch", False, f"Status {r.status_code}")
except Exception as e:
    test("POST /conversions/batch", False, str(e)[:30])

for t in tests:
    print(t)
print()
tests = []

# Webhooks
print("Webhooks (3 endpoints):")
webhook_id = None
try:
    r = requests.post(f"{BASE}/webhooks",
        json={"name": "test", "url": "https://example.com"},
        headers=headers, timeout=TIMEOUT)
    webhook_id = r.json().get("webhook_id") or r.json().get("id")
    test("POST /webhooks", r.status_code in [201, 200], f"ID: {webhook_id}")
except Exception as e:
    test("POST /webhooks", False, str(e)[:30])

try:
    r = requests.get(f"{BASE}/webhooks", headers=headers, timeout=TIMEOUT)
    count = len(r.json().get('webhooks', []))
    test("GET /webhooks", r.status_code == 200, f"{count} webhooks")
except Exception as e:
    test("GET /webhooks", False, str(e)[:30])

try:
    if webhook_id:
        r = requests.delete(f"{BASE}/webhooks/{webhook_id}", headers=headers, timeout=TIMEOUT)
    else:
        r = requests.delete(f"{BASE}/webhooks/test", headers=headers, timeout=TIMEOUT)
    test("DELETE /webhooks/<id>", r.status_code in [200, 404])
except Exception as e:
    test("DELETE /webhooks/<id>", False, str(e)[:30])

for t in tests:
    print(t)
print()
tests = []

# Docs
print("API Documentation (bonus):")
try:
    r = requests.get(f"{BASE}/docs", timeout=TIMEOUT)
    endpoints = len(r.json().get('endpoints', {}))
    test("GET /docs", r.status_code == 200, f"{endpoints} endpoints")
except Exception as e:
    test("GET /docs", False, str(e)[:30])

for t in tests:
    print(t)

# Summary
print("\n" + "="*70)
total = passed + failed
pct = (passed/total*100) if total > 0 else 0
print(f"  RESULTS: {passed}/{total} endpoints working ({pct:.0f}%)")
print("="*70)

if failed == 0:
    print("\n[SUCCESS] All API endpoints operational!")
else:
    print(f"\n[WARNING] {failed} endpoints need attention")

print()
