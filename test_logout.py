#!/usr/bin/env python3
"""
Test script to verify logout functionality
Run this after starting the backend server
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_logout():
    """Test the complete logout flow"""
    
    print("=" * 60)
    print("LOGOUT FUNCTIONALITY TEST")
    print("=" * 60)
    
    session = requests.Session()
    
    # Step 1: Register/Create user
    print("\n[1] Creating test user...")
    register_data = {
        'username': 'testuser_logout',
        'email': 'logout_test@example.com',
        'password': 'password123'
    }
    
    try:
        response = session.post(f'{BASE_URL}/api/auth/register', json=register_data)
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}")
        
        if response.status_code not in [200, 201]:
            print("    ⚠️  Registration failed, trying login instead...")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return
    
    # Step 2: Login
    print("\n[2] Logging in...")
    login_data = {
        'username': register_data['username'],
        'password': register_data['password']
    }
    
    try:
        response = session.post(f'{BASE_URL}/api/auth/login', json=login_data)
        print(f"    Status: {response.status_code}")
        resp_json = response.json()
        print(f"    Response: {resp_json}")
        
        if response.status_code != 200:
            print("    ❌ Login failed!")
            return
            
        user_id = resp_json.get('user_id')
        print(f"    ✓ Login successful! User ID: {user_id}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return
    
    # Step 3: Verify authenticated - call me endpoint
    print("\n[3] Verifying authenticated state...")
    try:
        response = session.get(f'{BASE_URL}/api/auth/me')
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}")
        
        if response.status_code == 200:
            print("    ✓ Authenticated!")
        else:
            print("    ❌ Not authenticated or endpoint failed")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Step 4: Logout
    print("\n[4] Logging out...")
    try:
        response = session.post(f'{BASE_URL}/api/auth/logout')
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}")
        
        if response.status_code == 200:
            print("    ✓ Logout successful!")
        else:
            print("    ❌ Logout failed!")
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return
    
    # Step 5: Verify logged out - should fail with 401
    print("\n[5] Verifying logged out state (should get 401)...")
    try:
        response = session.get(f'{BASE_URL}/api/auth/me')
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 401:
            print("    ✓ Correctly logged out! (Got 401 Unauthorized)")
        else:
            print("    ❌ Still authenticated! Session not cleared properly")
            print(f"    Response: {response.json()}")
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("""
If you see:
✓ Login successful
✓ Authenticated
✓ Logout successful
✓ Correctly logged out (Got 401)

Then logout is working properly! 🎉
    """)

if __name__ == '__main__':
    print("\nMake sure the backend server is running on port 5000")
    print("Command: pip install requests")
    print("Then: python test_logout.py\n")
    
    try:
        test_logout()
    except Exception as e:
        print(f"Test failed with error: {e}")
