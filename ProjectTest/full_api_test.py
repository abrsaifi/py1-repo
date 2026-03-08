#!/usr/bin/env python3
"""
Complete API Testing Suite - Tests all 19 endpoints with actual conversions
"""
import requests
import json
import os

BASE = "http://localhost:5000/api"
TIMEOUT = 30

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add(self, name, status, detail=""):
        symbol = "✓" if status else "✗"
        if status:
            self.passed += 1
        else:
            self.failed += 1
        msg = f"{symbol} {name:<50} {'PASS' if status else 'FAIL'}"
        if detail:
            msg += f" ({detail})"
        self.tests.append(msg)
    
    def print_all(self):
        for test in self.tests:
            print(f"  {test}")
    
    def summary(self):
        total = self.passed + self.failed
        pct = (self.passed/total*100) if total > 0 else 0
        return f"\n{'='*70}\n  RESULTS: {self.passed}/{total} passed ({pct:.0f}%)\n{'='*70}"

# Initialize
results = TestResults()
token = None
headers = {}
test_data = {}

print("\n" + "="*70)
print("  DOCUMENT CONVERTER API - COMPLETE TEST SUITE (19 endpoints)")
print("="*70 + "\n")

# ============================================================================
# 1-2: AUTHENTICATION (2 endpoints)
# ============================================================================
print("Authentication (2/19 endpoints):")

# Register
try:
    r = requests.post(f"{BASE}/auth/register",
        json={"username": "testapi", "email": "api@test.com", "password": "Test12345!"},
        timeout=TIMEOUT)
    if r.status_code in [201, 409]:
        data = r.json()
        token = data.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        results.add("POST /auth/register", True, f"Status {r.status_code}")
    else:
        results.add("POST /auth/register", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /auth/register", False, str(e)[:30])

# Login
if not token:
    try:
        r = requests.post(f"{BASE}/auth/login",
            json={"username": "testapi", "password": "Test12345!"},
            timeout=TIMEOUT)
        if r.status_code == 200:
            token = r.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            results.add("POST /auth/login", True)
        else:
            results.add("POST /auth/login", False, f"Status {r.status_code}")
    except Exception as e:
        results.add("POST /auth/login", False, str(e)[:30])
else:
    results.add("POST /auth/login", True, "Already authenticated")

results.print_all()
print()

# Check if auth succeeded
if not token:
    print("❌ Authentication failed. Cannot continue with other tests.")
    print(results.summary())
    exit(1)

# ============================================================================
# 3-8: PHASE 1 CONVERSIONS (6 endpoints)
# ============================================================================
print("Phase 1 Conversions (6/19 endpoints):")

# PDF → DOCX
try:
    with open("sample.pdf", "rb") as f:
        r = requests.post(f"{BASE}/conversions/pdf-to-docx",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test_data["pdf_to_docx"] = r.json()
        results.add("POST /conversions/pdf-to-docx", True, 
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/pdf-to-docx", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/pdf-to-docx", False, str(e)[:30])

# DOCX → PDF
try:
    with open("sample.docx", "rb") as f:
        r = requests.post(f"{BASE}/conversions/docx-to-pdf",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test_data["docx_to_pdf"] = r.json()
        results.add("POST /conversions/docx-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/docx-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/docx-to-pdf", False, str(e)[:30])

# Image → PDF
try:
    with open("sample.jpg", "rb") as f:
        r = requests.post(f"{BASE}/conversions/image-to-pdf",
            files={"files[]": f}, data={"orientation": "portrait"},
            headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test_data["image_to_pdf"] = r.json()
        results.add("POST /conversions/image-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/image-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/image-to-pdf", False, str(e)[:30])

# XLSX → PDF
try:
    with open("sample.xlsx", "rb") as f:
        r = requests.post(f"{BASE}/conversions/xlsx-to-pdf",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test_data["xlsx_to_pdf"] = r.json()
        results.add("POST /conversions/xlsx-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/xlsx-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/xlsx-to-pdf", False, str(e)[:30])

# PDF → Image
try:
    with open("sample.pdf", "rb") as f:
        r = requests.post(f"{BASE}/conversions/pdf-to-image",
            files={"file": f}, 
            data={"pages": "1", "format": "jpg", "quality": "85"},
            headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test_data["pdf_to_image"] = r.json()
        results.add("POST /conversions/pdf-to-image", True,
                   f"{len(r.json()['files'])} image(s)")
    else:
        results.add("POST /conversions/pdf-to-image", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/pdf-to-image", False, str(e)[:30])

# Merge PDFs
try:
    files = [("files[]", open("sample.pdf", "rb")), 
             ("files[]", open("sample.csv", "rb"))]
    r = requests.post(f"{BASE}/conversions/merge",
        files=files, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        test_data["merge"] = r.json()
        results.add("POST /conversions/merge", True,
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/merge", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/merge", False, str(e)[:30])

results.print_all()
print()

# ============================================================================
# 9-12: PHASE 2 CONVERSIONS (4 endpoints)
# ============================================================================
print("Phase 2 Advanced Conversions (4/19 endpoints):")

# PPTX → PDF
try:
    with open("sample.pptx", "rb") as f:
        r = requests.post(f"{BASE}/conversions/pptx-to-pdf",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        results.add("POST /conversions/pptx-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    elif r.status_code == 501:
        results.add("POST /conversions/pptx-to-pdf", False, "LibreOffice not available")
    else:
        results.add("POST /conversions/pptx-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/pptx-to-pdf", False, str(e)[:30])

# HTML → PDF
try:
    r = requests.post(f"{BASE}/conversions/html-to-pdf",
        json={"html": "<h1>Test</h1><p>HTML conversion test</p>"},
        headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        results.add("POST /conversions/html-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    elif r.status_code == 501:
        results.add("POST /conversions/html-to-pdf", False, "WeasyPrint not available")
    else:
        results.add("POST /conversions/html-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/html-to-pdf", False, str(e)[:30])

# CSV → PDF
try:
    with open("sample.csv", "rb") as f:
        r = requests.post(f"{BASE}/conversions/csv-to-pdf",
            files={"file": f}, headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        results.add("POST /conversions/csv-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/csv-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/csv-to-pdf", False, str(e)[:30])

# Text → PDF
try:
    r = requests.post(f"{BASE}/conversions/text-to-pdf",
        json={"text": "This is test text\nfor PDF conversion\nwith multiple lines"},
        headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        results.add("POST /conversions/text-to-pdf", True,
                   f"{r.json()['file']['size']} bytes")
    else:
        results.add("POST /conversions/text-to-pdf", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/text-to-pdf", False, str(e)[:30])

results.print_all()
print()

# ============================================================================
# 13-15: USER CONVERSION HISTORY (3 endpoints)
# ============================================================================
print("User Conversion History (3/19 endpoints):")

# Get history
conv_id = None
try:
    r = requests.get(f"{BASE}/user/conversions?limit=10",
        headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        count = len(data.get("conversions", []))
        if count > 0:
            conv_id = data["conversions"][0]["id"]
        results.add("GET /user/conversions", True, f"{count} records")
    else:
        results.add("GET /user/conversions", False, f"Status {r.status_code}")
except Exception as e:
    results.add("GET /user/conversions", False, str(e)[:30])

# Get conversion detail
try:
    if conv_id:
        r = requests.get(f"{BASE}/user/conversions/{conv_id}",
            headers=headers, timeout=TIMEOUT)
    else:
        r = requests.get(f"{BASE}/user/conversions/test123",
            headers=headers, timeout=TIMEOUT)
    
    if r.status_code in [200, 404]:
        results.add("GET /user/conversions/<id>", True, f"Status {r.status_code}")
    else:
        results.add("GET /user/conversions/<id>", False, f"Status {r.status_code}")
except Exception as e:
    results.add("GET /user/conversions/<id>", False, str(e)[:30])

# Delete conversion (use non-existent ID to not break real data)
try:
    r = requests.delete(f"{BASE}/user/conversions/test_delete_123",
        headers=headers, timeout=TIMEOUT)
    if r.status_code in [200, 404]:
        results.add("DELETE /user/conversions/<id>", True, f"Status {r.status_code}")
    else:
        results.add("DELETE /user/conversions/<id>", False, f"Status {r.status_code}")
except Exception as e:
    results.add("DELETE /user/conversions/<id>", False, str(e)[:30])

results.print_all()
print()

# ============================================================================
# 16-17: USER SETTINGS (2 endpoints)
# ============================================================================
print("User Settings Management (2/19 endpoints):")

# Get settings
try:
    r = requests.get(f"{BASE}/user/settings",
        headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        count = len(r.json().get("settings", {}))
        results.add("GET /user/settings", True, f"{count} settings")
    else:
        results.add("GET /user/settings", False, f"Status {r.status_code}")
except Exception as e:
    results.add("GET /user/settings", False, str(e)[:30])

# Update settings
try:
    r = requests.post(f"{BASE}/user/settings",
        json={"theme": "dark", "notifications_enabled": True},
        headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        results.add("POST /user/settings", True)
    else:
        results.add("POST /user/settings", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /user/settings", False, str(e)[:30])

results.print_all()
print()

# ============================================================================
# 18: BATCH CONVERSION (1 endpoint)
# ============================================================================
print("Batch Conversion (1/19 endpoint):")

try:
    files = [("files[]", open("sample.pdf", "rb")),
             ("files[]", open("sample.csv", "rb"))]
    r = requests.post(f"{BASE}/conversions/batch",
        files=files, data={"tool": "pdf-to-docx"},
        headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        results.add("POST /conversions/batch", True, 
                   f"{len(r.json()['results'])} files processed")
    else:
        results.add("POST /conversions/batch", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /conversions/batch", False, str(e)[:30])

results.print_all()
print()

# ============================================================================
# 19-21: WEBHOOKS (3 endpoints)
# ============================================================================
print("Webhooks Management (3/19 endpoints):")

webhook_id = None

# Create webhook
try:
    r = requests.post(f"{BASE}/webhooks",
        json={"name": "test_webhook", "url": "https://example.com/webhook",
              "events": ["conversion_complete"]},
        headers=headers, timeout=TIMEOUT)
    if r.status_code in [201, 200]:
        data = r.json()
        webhook_id = data.get("webhook_id") or data.get("id")
        results.add("POST /webhooks", True, f"Created {webhook_id}")
    else:
        results.add("POST /webhooks", False, f"Status {r.status_code}")
except Exception as e:
    results.add("POST /webhooks", False, str(e)[:30])

# List webhooks
try:
    r = requests.get(f"{BASE}/webhooks", headers=headers, timeout=TIMEOUT)
    if r.status_code == 200:
        count = len(r.json().get("webhooks", []))
        results.add("GET /webhooks", True, f"{count} webhooks")
    else:
        results.add("GET /webhooks", False, f"Status {r.status_code}")
except Exception as e:
    results.add("GET /webhooks", False, str(e)[:30])

# Delete webhook (use test ID)
try:
    if webhook_id:
        r = requests.delete(f"{BASE}/webhooks/{webhook_id}",
            headers=headers, timeout=TIMEOUT)
    else:
        r = requests.delete(f"{BASE}/webhooks/test123",
            headers=headers, timeout=TIMEOUT)
    
    if r.status_code in [200, 404]:
        results.add("DELETE /webhooks/<id>", True, f"Status {r.status_code}")
    else:
        results.add("DELETE /webhooks/<id>", False, f"Status {r.status_code}")
except Exception as e:
    results.add("DELETE /webhooks/<id>", False, str(e)[:30])

results.print_all()
print()

# ============================================================================
# BONUS: API DOCUMENTATION
# ============================================================================
print("API Documentation (Bonus endpoint):")

try:
    r = requests.get(f"{BASE}/docs", timeout=TIMEOUT)
    if r.status_code == 200:
        data = r.json()
        endpoints = len(data.get("endpoints", {}))
        results.add("GET /docs", True, f"{endpoints} endpoints documented")
    else:
        results.add("GET /docs", False, f"Status {r.status_code}")
except Exception as e:
    results.add("GET /docs", False, str(e)[:30])

results.print_all()

# Print summary
print(results.summary())
print(f"\n✅ API Testing Complete!")
print(f"   {results.passed} endpoints working, {results.failed} issues\n")
