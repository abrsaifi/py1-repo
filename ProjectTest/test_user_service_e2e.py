"""
User Service End-to-End Tests
Comprehensive test suite for User Service endpoints.

Run with: python ProjectTest/test_user_service_e2e.py
"""

import requests
import json
import time
from datetime import datetime, timezone

# Configuration
AUTH_SERVICE_URL = 'http://localhost:5001'
USER_SERVICE_URL = 'http://localhost:5002'
GATEWAY_URL = 'http://localhost:5000'

# Test user credentials
TEST_USER = {
    'username': f'testuser_phase3_{int(time.time())}',
    'email': f'testuser_{int(time.time())}@example.com',
    'password': 'TestPassword123!',
    'full_name': 'Test User Phase 3',
}

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_test(test_name, passed, details=""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status} - {test_name}")
    if details:
        print(f"      {YELLOW}{details}{RESET}")


def test_1_auth_service_health():
    """Test 1: Auth Service Health Check"""
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/auth/health", timeout=5)
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = data.get('status') == 'healthy'
        
        print_test("Auth Service Health", passed)
        return passed, None
    except Exception as e:
        print_test("Auth Service Health", False, str(e))
        return False, str(e)


def test_2_user_service_health():
    """Test 2: User Service Health Check"""
    try:
        resp = requests.get(f"{USER_SERVICE_URL}/user/health", timeout=5)
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = data.get('status') == 'healthy'
        
        print_test("User Service Health", passed)
        return passed, None
    except Exception as e:
        print_test("User Service Health", False, str(e))
        return False, str(e)


def test_3_api_gateway_health():
    """Test 3: API Gateway Health Check"""
    try:
        resp = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = (
                data.get('status') == 'healthy' and
                'services' in data and
                'user' in data['services']
            )
        
        print_test("API Gateway Health", passed)
        return passed, None
    except Exception as e:
        print_test("API Gateway Health", False, str(e))
        return False, str(e)


def test_4_user_registration():
    """Test 4: User Registration"""
    try:
        payload = {
            'username': TEST_USER['username'],
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'full_name': TEST_USER['full_name'],
        }
        
        resp = requests.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            json=payload,
            timeout=5
        )
        
        passed = resp.status_code == 201
        
        if passed:
            data = resp.json()
            TEST_USER['user_id'] = data.get('user_id')
            TEST_USER['access_token'] = data.get('access_token')
            passed = TEST_USER['user_id'] and TEST_USER['access_token']
        
        print_test("User Registration", passed)
        return passed, TEST_USER.get('user_id')
    except Exception as e:
        print_test("User Registration", False, str(e))
        return False, None


def test_5_get_profile():
    """Test 5: Get User Profile"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/profile",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = 'user' in data and 'profile' in data
        
        print_test("Get User Profile", passed)
        return passed, None
    except Exception as e:
        print_test("Get User Profile", False, str(e))
        return False, None


def test_6_update_profile():
    """Test 6: Update User Profile"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        payload = {
            'company': 'Acme Corp',
            'job_title': 'Senior Engineer',
            'location': 'San Francisco, CA',
            'bio': 'Software engineer passionate about cloud infrastructure',
            'website_url': 'https://example.com',
            'github_username': 'testuser',
            'linkedin_username': 'testuser',
        }
        
        resp = requests.put(
            f"{GATEWAY_URL}/user/profile",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            profile = data.get('profile', {})
            passed = (
                profile.get('company') == 'Acme Corp' and
                profile.get('job_title') == 'Senior Engineer'
            )
        
        print_test("Update User Profile", passed)
        return passed, None
    except Exception as e:
        print_test("Update User Profile", False, str(e))
        return False, None


def test_7_get_preferences():
    """Test 7: Get User Preferences"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/preferences",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = (
                'theme' in data and
                'language' in data and
                'timezone' in data
            )
        
        print_test("Get User Preferences", passed)
        return passed, None
    except Exception as e:
        print_test("Get User Preferences", False, str(e))
        return False, None


def test_8_update_preferences():
    """Test 8: Update User Preferences"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        payload = {
            'theme': 'dark',
            'language': 'en',
            'timezone': 'America/Los_Angeles',
            'email_notifications': True,
            'newsletter': False,
            'session_timeout_minutes': 120,
        }
        
        resp = requests.put(
            f"{GATEWAY_URL}/user/preferences",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            prefs = data.get('preferences', {})
            passed = (
                prefs.get('theme') == 'dark' and
                prefs.get('timezone') == 'America/Los_Angeles'
            )
        
        print_test("Update User Preferences", passed)
        return passed, None
    except Exception as e:
        print_test("Update User Preferences", False, str(e))
        return False, None


def test_9_get_activity_history():
    """Test 9: Get Activity History"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/activity?limit=10&offset=0",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = (
                'activities' in data and
                'total' in data and
                isinstance(data['activities'], list)
            )
        
        print_test("Get Activity History", passed)
        return passed, None
    except Exception as e:
        print_test("Get Activity History", False, str(e))
        return False, None


def test_10_get_usage_stats():
    """Test 10: Get Current Usage Statistics"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/usage/current",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = (
                'period_type' in data and
                'conversion_count' in data and
                'total_input_size_bytes' in data
            )
        
        print_test("Get Usage Statistics", passed)
        return passed, None
    except Exception as e:
        print_test("Get Usage Statistics", False, str(e))
        return False, None


def test_11_change_email():
    """Test 11: Change Email Address"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        new_email = f"newemail_{int(time.time())}@example.com"
        
        payload = {'new_email': new_email}
        
        resp = requests.put(
            f"{GATEWAY_URL}/user/email",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            user = data.get('user', {})
            passed = user.get('email') == new_email
        
        print_test("Change Email Address", passed)
        return passed, None
    except Exception as e:
        print_test("Change Email Address", False, str(e))
        return False, None


def test_12_unauthorized_access():
    """Test 12: Unauthorized Access (No Token)"""
    try:
        resp = requests.get(
            f"{GATEWAY_URL}/user/profile",
            timeout=5
        )
        
        passed = resp.status_code == 401
        
        print_test("Unauthorized Access Denied", passed)
        return passed, None
    except Exception as e:
        print_test("Unauthorized Access Denied", False, str(e))
        return False, None


def test_13_invalid_token():
    """Test 13: Invalid Token Rejection"""
    try:
        headers = {'Authorization': 'Bearer invalid.token.here'}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/profile",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 401
        
        print_test("Invalid Token Rejected", passed)
        return passed, None
    except Exception as e:
        print_test("Invalid Token Rejected", False, str(e))
        return False, None


def test_14_get_devices():
    """Test 14: Get Trusted Devices"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/devices",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = 'devices' in data and 'count' in data
        
        print_test("Get Trusted Devices", passed)
        return passed, None
    except Exception as e:
        print_test("Get Trusted Devices", False, str(e))
        return False, None


def test_15_get_usage_history():
    """Test 15: Get Usage History"""
    try:
        headers = {'Authorization': f"Bearer {TEST_USER['access_token']}"}
        
        resp = requests.get(
            f"{GATEWAY_URL}/user/usage/history?months=12",
            headers=headers,
            timeout=5
        )
        
        passed = resp.status_code == 200
        
        if passed:
            data = resp.json()
            passed = 'history' in data and 'count' in data
        
        print_test("Get Usage History", passed)
        return passed, None
    except Exception as e:
        print_test("Get Usage History", False, str(e))
        return False, None


def run_all_tests():
    """Run all test cases"""
    
    print_header("USER SERVICE END-TO-END TESTS")
    print(f"Execution Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    tests = [
        ("Auth Service Health", test_1_auth_service_health),
        ("User Service Health", test_2_user_service_health),
        ("API Gateway Health", test_3_api_gateway_health),
        ("User Registration", test_4_user_registration),
        ("Get User Profile", test_5_get_profile),
        ("Update User Profile", test_6_update_profile),
        ("Get User Preferences", test_7_get_preferences),
        ("Update User Preferences", test_8_update_preferences),
        ("Get Activity History", test_9_get_activity_history),
        ("Get Usage Statistics", test_10_get_usage_stats),
        ("Change Email Address", test_11_change_email),
        ("Unauthorized Access Denied", test_12_unauthorized_access),
        ("Invalid Token Rejected", test_13_invalid_token),
        ("Get Trusted Devices", test_14_get_devices),
        ("Get Usage History", test_15_get_usage_history),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed, data = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print_test(test_name, False, str(e))
            results.append((test_name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    pass_percentage = (passed_count / total_count * 100) if total_count > 0 else 0
    
    for test_name, passed in results:
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {status} {test_name}")
    
    print(f"\n  {BOLD}Total: {passed_count}/{total_count} passed ({pass_percentage:.1f}%){RESET}")
    
    if passed_count == total_count:
        print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}\n")
    else:
        failed = [name for name, passed in results if not passed]
        print(f"\n{RED}{BOLD}✗ TESTS FAILED:{RESET}")
        for name in failed:
            print(f"  {RED}- {name}{RESET}")
        print()
    
    return passed_count == total_count


if __name__ == '__main__':
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        exit(1)
    except Exception as e:
        print(f"{RED}Test execution error: {e}{RESET}")
        exit(1)
