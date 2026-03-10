#!/usr/bin/env python3
"""Test the 3 remaining failing endpoints"""
import requests
import json
import time

BASE = "http://localhost:5000/api"

def test_register():
    """Test registration with unique user"""
    print("\n=== TEST 1: Register ===")
    try:
        ts = int(time.time() * 1000) % 100000
        username = f"testuser{ts}"
        email = f"test{ts}@example.com"
        
        resp = requests.post(f"{BASE}/auth/register", json={
            "username": username,
            "email": email, 
            "password": "Password123"
        })
        print(f"Status: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        
        if resp.status_code in [201, 200]:
            return resp.json().get('token')
        return None
    except Exception as e:
        print(f"Error: {e}")
    return None

def test_pptx(token):
    """Test PPTX conversion"""
    print("\n=== TEST 2: PPTX-to-PDF ===")
    if not token:
        print("Skipped - no token available")
        return
    
    try:
        with open("sample.pptx", "rb") as f:
            resp = requests.post(f"{BASE}/conversions/pptx-to-pdf",
                files={"file": f},
                headers={"Authorization": f"Bearer {token}"})
        
        print(f"Status: {resp.status_code}")
        try:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"Response (text): {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

def test_html(token):
    """Test HTML conversion"""
    print("\n=== TEST 3: HTML-to-PDF ===")
    if not token:
        print("Skipped - no token available")
        return
    
    try:
        resp = requests.post(f"{BASE}/conversions/html-to-pdf",
            json={"html": "<h1>Test</h1>"},
            headers={"Authorization": f"Bearer {token}"})
        
        print(f"Status: {resp.status_code}")
        try:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"Response (text): {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    token = test_register()
    test_pptx(token)
    test_html(token)
