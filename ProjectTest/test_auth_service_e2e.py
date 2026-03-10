"""
Auth Service End-to-End Test
Tests registration, login, token verification, and user endpoints.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
GATEWAY_URL = "http://localhost:5000"
AUTH_SERVICE_URL = "http://localhost:5001"

# Test data
TEST_USER = {
    "username": f"testuser_{int(time.time())}",
    "email": f"test_{int(time.time())}@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
}

COLORS = {
    'GREEN': '\033[92m',
    'RED': '\033[91m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'RESET': '\033[0m'
}


def print_header(text):
    """Print section header"""
    print(f"\n{COLORS['BLUE']}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{COLORS['RESET']}\n")


def print_success(text):
    """Print success message"""
    print(f"{COLORS['GREEN']}✓ {text}{COLORS['RESET']}")


def print_error(text):
    """Print error message"""
    print(f"{COLORS['RED']}✗ {text}{COLORS['RESET']}")


def print_info(text):
    """Print info message"""
    print(f"{COLORS['YELLOW']}ℹ {text}{COLORS['RESET']}")


def test_auth_service_health():
    """Test 1: Check auth service health"""
    print_header("Test 1: Auth Service Health Check")
    
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/auth/health", timeout=5)
        
        if resp.status_code != 200:
            print_error(f"Health check failed: {resp.status_code}")
            return False
        
        data = resp.json()
        print_info(f"Status: {data.get('status')}")
        print_info(f"Database: {data.get('database')}")
        print_success("Auth service is healthy")
        return True
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to auth service on port 5001")
        print_info("Make sure auth service is running: python services/auth-service/main.py")
        return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def test_api_gateway_health():
    """Test 2: Check API Gateway health"""
    print_header("Test 2: API Gateway Health Check")
    
    try:
        resp = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        
        if resp.status_code != 200:
            print_error(f"Health check failed: {resp.status_code}")
            return False
        
        data = resp.json()
        print_info(f"Status: {data.get('status')}")
        print_info(f"Database: {data.get('database')}")
        print_info(f"Redis: {data.get('redis')}")
        
        # Check service status
        services = data.get('services', {})
        for service, status in services.items():
            if status == 'healthy':
                print_success(f"{service}: {status}")
            else:
                print_info(f"{service}: {status}")
        
        print_success("API Gateway is healthy")
        return True
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API Gateway on port 5000")
        print_info("Make sure API Gateway is running: python services/api-gateway/main.py")
        return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def test_user_registration():
    """Test 3: User registration"""
    print_header("Test 3: User Registration")
    
    print_info(f"Username: {TEST_USER['username']}")
    print_info(f"Email: {TEST_USER['email']}")
    
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/auth/register",
            json=TEST_USER,
            timeout=10
        )
        
        if resp.status_code != 201:
            print_error(f"Registration failed: {resp.status_code}")
            print_info(f"Response: {resp.text}")
            return None
        
        data = resp.json()
        user_id = data.get('user_id')
        access_token = data.get('access_token')
        
        print_success(f"User registered: {user_id}")
        print_success(f"Access token received")
        print_info(f"Token (first 50 chars): {access_token[:50]}...")
        
        return {
            'user_id': user_id,
            'access_token': access_token,
            'username': TEST_USER['username']
        }
    
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None


def test_user_login():
    """Test 4: User login (existing user)"""
    print_header("Test 4: User Login")
    
    login_data = {
        "username": TEST_USER['username'],
        "password": TEST_USER['password']
    }
    
    print_info(f"Username: {login_data['username']}")
    
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if resp.status_code != 200:
            print_error(f"Login failed: {resp.status_code}")
            print_info(f"Response: {resp.text}")
            return None
        
        data = resp.json()
        access_token = data.get('access_token')
        user_id = data.get('user_id')
        
        print_success(f"User logged in: {user_id}")
        print_success(f"New access token received")
        print_info(f"Subscription tier: {data.get('subscription_tier')}")
        
        return {
            'user_id': user_id,
            'access_token': access_token,
            'username': data.get('username')
        }
    
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None


def test_token_verification(access_token):
    """Test 5: Token verification"""
    print_header("Test 5: Token Verification")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/auth/verify",
            headers=headers,
            json={'token': access_token},
            timeout=10
        )
        
        if resp.status_code != 200:
            print_error(f"Token verification failed: {resp.status_code}")
            return False
        
        data = resp.json()
        
        if not data.get('valid'):
            print_error("Token is invalid")
            return False
        
        print_success("Token is valid")
        print_info(f"User ID: {data.get('user_id')}")
        print_info(f"Username: {data.get('username')}")
        print_info(f"Role: {data.get('role')}")
        
        return True
    
    except Exception as e:
        print_error(f"Token verification error: {str(e)}")
        return False


def test_get_user_info(access_token):
    """Test 6: Get current user info"""
    print_header("Test 6: Get Current User Info")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        resp = requests.get(
            f"{GATEWAY_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code != 200:
            print_error(f"Failed to get user info: {resp.status_code}")
            return False
        
        data = resp.json()
        
        print_success("User info retrieved")
        print_info(f"Username: {data.get('username')}")
        print_info(f"Email: {data.get('email')}")
        print_info(f"Full Name: {data.get('full_name')}")
        print_info(f"Subscription Tier: {data.get('subscription_tier')}")
        print_info(f"Created At: {data.get('created_at')}")
        
        return True
    
    except Exception as e:
        print_error(f"Get user info error: {str(e)}")
        return False


def test_user_logout(access_token):
    """Test 7: User logout"""
    print_header("Test 7: User Logout")
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/auth/logout",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code != 200:
            print_error(f"Logout failed: {resp.status_code}")
            return False
        
        print_success("User logged out successfully")
        return True
    
    except Exception as e:
        print_error(f"Logout error: {str(e)}")
        return False


def test_invalid_token():
    """Test 8: Test with invalid token"""
    print_header("Test 8: Invalid Token Handling")
    
    headers = {
        'Authorization': 'Bearer invalid_token_12345'
    }
    
    try:
        resp = requests.get(
            f"{GATEWAY_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        if resp.status_code == 401:
            print_success("Invalid token correctly rejected")
            return True
        else:
            print_error(f"Expected 401 status, got {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Invalid token test error: {str(e)}")
        return False


def test_missing_auth_header():
    """Test 9: Test missing authorization header"""
    print_header("Test 9: Missing Authorization Header")
    
    try:
        resp = requests.get(
            f"{GATEWAY_URL}/auth/me",
            timeout=10
        )
        
        if resp.status_code == 401:
            print_success("Missing auth header correctly rejected")
            data = resp.json()
            print_info(f"Error: {data.get('error')}")
            return True
        else:
            print_error(f"Expected 401 status, got {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Missing header test error: {str(e)}")
        return False


def test_invalid_credentials():
    """Test 10: Test with invalid credentials"""
    print_header("Test 10: Invalid Credentials")
    
    login_data = {
        "username": "nonexistent_user_xyz",
        "password": "wrong_password"
    }
    
    try:
        resp = requests.post(
            f"{GATEWAY_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if resp.status_code == 401:
            print_success("Invalid credentials correctly rejected")
            data = resp.json()
            print_info(f"Error: {data.get('error')}")
            return True
        else:
            print_error(f"Expected 401 status, got {resp.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Invalid credentials test error: {str(e)}")
        return False


# ===== Main Test Runner =====

def main():
    """Run all tests"""
    print(f"\n{COLORS['BLUE']}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        AUTH SERVICE END-TO-END TEST SUITE                ║")
    print("║                                                           ║")
    print(f"║  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{COLORS['RESET']}\n")
    
    results = {}
    
    # Test 1: Auth service health
    results['auth_health'] = test_auth_service_health()
    if not results['auth_health']:
        print_error("Cannot proceed - auth service is not available")
        return
    
    # Test 2: API Gateway health
    results['gateway_health'] = test_api_gateway_health()
    if not results['gateway_health']:
        print_error("Cannot proceed - API Gateway is not available")
        return
    
    # Test 3: Registration
    user_data = test_user_registration()
    results['registration'] = user_data is not None
    if not user_data:
        print_error("Cannot continue - registration failed")
        return
    
    # Test 4: Login
    login_data = test_user_login()
    results['login'] = login_data is not None
    if not login_data:
        print_error("Cannot continue - login failed")
        return
    
    # Test 5: Token verification
    results['token_verify'] = test_token_verification(login_data['access_token'])
    
    # Test 6: Get user info
    results['get_user'] = test_get_user_info(login_data['access_token'])
    
    # Test 7: Logout
    results['logout'] = test_user_logout(login_data['access_token'])
    
    # Test 8: Invalid token
    results['invalid_token'] = test_invalid_token()
    
    # Test 9: Missing header
    results['missing_header'] = test_missing_auth_header()
    
    # Test 10: Invalid credentials
    results['invalid_creds'] = test_invalid_credentials()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        icon = "✓" if result else "✗"
        color = COLORS['GREEN'] if result else COLORS['RED']
        
        print(f"{color}{icon} {test_name.upper()}: {status}{COLORS['RESET']}")
    
    print(f"\n{COLORS['BLUE']}{'='*60}{COLORS['RESET']}")
    
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total})")
        print(f"{COLORS['BLUE']}{'='*60}{COLORS['RESET']}\n")
        return 0
    else:
        print_error(f"SOME TESTS FAILED ({passed}/{total})")
        print(f"{COLORS['BLUE']}{'='*60}{COLORS['RESET']}\n")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
