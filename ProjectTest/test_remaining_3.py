#!/usr/bin/env python3
"""Test the 3 remaining failing endpoints"""
import requests
import json
import time

BASE = \"http://localhost:5000/api\"

def test_register():
    \"\"\"Test registration\"\"\"
    print(\"\\n=== TEST 1: Register ===\")
    try:
        # Use unique username with timestamp
        ts = int(time.time() * 1000) % 100000
        username = f\"testuser{ts}\"
        email = f\"test{ts}@example.com\"
        
        resp = requests.post(f\"{BASE}/auth/register\", json={
            \"username\": username,
            \"email\": email, 
            "password": "Password123"
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_pptx():
    """Test PPTX conversion"""
    print("\n=== TEST 2: PPTX-to-PDF ===")
    try:
        # Get token from newuser123 (just registered)
        resp1 = requests.post(f\"{BASE}/auth/login\", json={
            \"username\": \"newuser123\",
            \"password\": \"Password123\"
        })
        data = resp1.json()
        if resp1.status_code != 200:
            print(f\"Login failed: {data}\")
            return
        token = data.get('token')
        print(f"Token: {token[:20] if token else 'NO TOKEN'}...")
        
        # Try conversion
        with open("sample.pptx", "rb") as f:
            resp2 = requests.post(f"{BASE}/conversions/pptx-to-pdf",
                files={"file": f},
                headers={"Authorization": f"Bearer {token}"})
        
        print(f"Status: {resp2.status_code}")
        try:
            print(f"Response: {json.dumps(resp2.json(), indent=2)}")
        except:
            print(f"Response (text): {resp2.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

def test_html():
    """Test HTML conversion"""
    print("\n=== TEST 3: HTML-to-PDF ===")
    try:
        # Get token from newuser123  
        resp1 = requests.post(f\"{BASE}/auth/login\", json={
            \"username\": \"newuser123\",
            \"password\": \"Password123\"
        })
        data = resp1.json()
        if resp1.status_code != 200:
            print(f\"Login failed: {data}\")
            return
        token = data.get('token')
        
        # Try conversion
        resp2 = requests.post(f"{BASE}/conversions/html-to-pdf",
            json={"html": "<h1>Test</h1>"},
            headers={"Authorization": f"Bearer {token}"})
        
        print(f"Status: {resp2.status_code}")
        try:
            print(f"Response: {json.dumps(resp2.json(), indent=2)}")
        except:
            print(f"Response (text): {resp2.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_register()
    test_pptx()
    test_html()
