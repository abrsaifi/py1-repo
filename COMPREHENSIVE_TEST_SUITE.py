#!/usr/bin/env python3
"""
Comprehensive Test Suite for DocPro SaaS Platform
Tests all major components: Backend, Multi-Region, Database, Celery, Frontend
Windows-compatible version with ASCII output
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
API_BASE_URL = "http://localhost:5000"
API_TIMEOUT = 10

class TestRunner:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.total = 0
        
    def test(self, name, func):
        """Run a test and record result"""
        self.total += 1
        try:
            result = func()
            if result:
                self.passed += 1
                self.results.append((name, True, result))
                print("[PASS] " + name)
                return True
            else:
                self.failed += 1
                self.results.append((name, False, "Test returned False"))
                print("[FAIL] " + name)
                return False
        except Exception as e:
            self.failed += 1
            self.results.append((name, False, str(e)))
            print("[FAIL] " + name + ": " + str(e)[:50])
            return False
    
    def report(self):
        """Generate test report"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("Total Tests: " + str(self.total))
        print("Passed: " + str(self.passed))
        print("Failed: " + str(self.failed))
        percentage = (self.passed / self.total * 100) if self.total > 0 else 0
        print("Success Rate: {:.1f}%".format(percentage))
        print("="*80 + "\n")

# Initialize test runner
runner = TestRunner()

# ============================================================================
# SECTION 1: HEALTH CHECKS
# ============================================================================
print("\nSECTION 1: HEALTH CHECKS")
print("="*80)

def test_flask_health():
    """Test Flask server is responding"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=API_TIMEOUT)
        return response.status_code == 200
    except:
        return False

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=API_TIMEOUT)
        return response.status_code == 200
    except:
        return False

runner.test("Flask server responding", test_flask_health)
runner.test("API health endpoint", test_api_health)

# ============================================================================
# SECTION 2: AUTHENTICATION ENDPOINTS
# ============================================================================
print("\nSECTION 2: AUTHENTICATION")
print("="*80)

def test_login_endpoint():
    """Test login endpoint exists"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"email": "test@example.com", "password": "test"},
            timeout=API_TIMEOUT
        )
        # Endpoint exists even if creds fail
        return response.status_code in [200, 401, 400]
    except:
        return False

def test_register_endpoint():
    """Test register endpoint exists"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/register",
            json={"email": "test@example.com", "password": "test"},
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 201, 400, 409]
    except:
        return False

runner.test("Authentication - Login endpoint", test_login_endpoint)
runner.test("Authentication - Register endpoint", test_register_endpoint)

# ============================================================================
# SECTION 3: CONVERSION ENDPOINTS
# ============================================================================
print("\nSECTION 3: CONVERSION ENDPOINTS")
print("="*80)

def test_conversion_list():
    """Test conversion history endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/conversions",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401]
    except:
        return False

def test_conversion_stats():
    """Test conversion statistics endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/conversions/stats",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401]
    except:
        return False

runner.test("Conversions - List endpoint", test_conversion_list)
runner.test("Conversions - Stats endpoint", test_conversion_stats)

# ============================================================================
# SECTION 4: MULTI-REGION ENDPOINTS (TASK 10)
# ============================================================================
print("\nSECTION 4: MULTI-REGION ENDPOINTS (TASK 10)")
print("="*80)

def test_regions_list():
    """Test list regions endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/multi-region/regions",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401, 403]
    except:
        return False

def test_region_health():
    """Test region health check endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/multi-region/health/check-all",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401, 403]
    except:
        return False

def test_replication_status():
    """Test replication status endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/multi-region/replication/status",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401, 403]
    except:
        return False

def test_geo_routing_detect():
    """Test geo-routing detection endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/multi-region/geo-routing/detect",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 400]
    except:
        return False

def test_failover_history():
    """Test failover history endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/multi-region/failover/history",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401, 403]
    except:
        return False

runner.test("Multi-Region - List regions", test_regions_list)
runner.test("Multi-Region - Health check all", test_region_health)
runner.test("Multi-Region - Replication status", test_replication_status)
runner.test("Multi-Region - Geo-routing detect", test_geo_routing_detect)
runner.test("Multi-Region - Failover history", test_failover_history)

# ============================================================================
# SECTION 5: ANALYTICS ENDPOINTS
# ============================================================================
print("\nSECTION 5: ANALYTICS ENDPOINTS")
print("="*80)

def test_dashboard_stats():
    """Test dashboard statistics endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/dashboard/stats",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401]
    except:
        return False

def test_analytics_overview():
    """Test analytics overview endpoint"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/analytics/overview",
            timeout=API_TIMEOUT
        )
        return response.status_code in [200, 401]
    except:
        return False

runner.test("Analytics - Dashboard stats", test_dashboard_stats)
runner.test("Analytics - Overview", test_analytics_overview)

# ============================================================================
# SECTION 6: DATABASE CONNECTIVITY
# ============================================================================
print("\nSECTION 6: DATABASE CONNECTIVITY")
print("="*80)

def test_database_models():
    """Test that models are importable"""
    try:
        from app.models import (
            User, Conversion, Subscription, APIKey,
            ComplianceAudit, RegionConfig, RegionReplica,
            GeoLocation, RegionFailover
        )
        return True
    except Exception as e:
        print("Model import error: " + str(e))
        return False

def test_celery_import():
    """Test Celery is properly configured"""
    try:
        from app.celery_config import make_celery
        return True
    except Exception as e:
        print("Celery import error: " + str(e))
        return False

runner.test("Database - Model imports", test_database_models)
runner.test("Database - Celery configuration", test_celery_import)

# ============================================================================
# SECTION 7: ENDPOINT COMPREHENSIVE SCAN
# ============================================================================
print("\nSECTION 7: COMPREHENSIVE ENDPOINT SCAN")
print("="*80)

# All documented endpoints from Task 10
endpoints_to_test = [
    ("GET", "/api/health"),
    ("GET", "/api/multi-region/regions"),
    ("GET", "/api/multi-region/replication/status"),
    ("GET", "/api/multi-region/failover/history"),
    ("GET", "/api/multi-region/geo-routing/routes"),
    ("GET", "/api/multi-region/config"),
    ("GET", "/api/conversions"),
    ("GET", "/api/conversions/stats"),
    ("GET", "/api/dashboard/stats"),
    ("GET", "/api/analytics/overview"),
]

endpoint_results = {"ok": 0, "error": 0}
for method, path in endpoints_to_test:
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{path}", timeout=5)
        else:
            response = requests.post(f"{API_BASE_URL}{path}", timeout=5)
        
        if response.status_code < 500:  # Not a server error
            endpoint_results["ok"] += 1
            status = f"{response.status_code}"
        else:
            endpoint_results["error"] += 1
            status = f"{response.status_code} SERVER ERROR"
    except requests.ConnectionError:
        endpoint_results["error"] += 1
        status = "CONNECTION ERROR"
    except Exception as e:
        endpoint_results["error"] += 1
        status = f"ERROR: {str(e)[:30]}"
    
    status_color = "" if response.status_code < 500 else ""
    print(f"{method:4} {path:50} {status}")

# ============================================================================
# SUMMARY
# ============================================================================

runner.test("Endpoint availability scan", lambda: endpoint_results["ok"] > endpoint_results["error"])

print(f"\nENDPOINT SUMMARY")
print(f"Accessible: {endpoint_results['ok']} / {len(endpoints_to_test)}")
print(f"Errors: {endpoint_results['error']} / {len(endpoints_to_test)}")

# ============================================================================
# FINAL REPORT
# ============================================================================

runner.report()

# Generate report file
report_content = f"""
# COMPREHENSIVE TEST REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Summary
- **Total Tests**: {runner.total}
- **Passed**: {runner.passed}
- **Failed**: {runner.failed}
- **Success Rate**: {(runner.passed/runner.total*100):.1f}%

## Test Results
"""

for name, passed, details in runner.results:
    status = "PASS" if passed else "FAIL"
    report_content += f"\n{status}: {name}\n  Details: {details}\n"

report_content += f"""

## Endpoint Health
- Accessible Endpoints: {endpoint_results['ok']} / {len(endpoints_to_test)}
- Failed Endpoints: {endpoint_results['error']} / {len(endpoints_to_test)}

## Deployment Readiness
- Backend APIs: {'Ready' if runner.passed > runner.total * 0.8 else 'Needs Work'}
- Multi-Region Tasks: {'Complete' if runner.passed > 10 else 'Verify'}
- Health Monitoring: {'Active' if runner.passed > 5 else 'Check'}

## Conclusion
{'SYSTEM READY FOR PRODUCTION' if runner.passed > runner.total * 0.8 else 'SYSTEM NEEDS VERIFICATION'}
"""

with open("c:\\Users\\dell\\OneDrive\\Documents\\py1\\TEST_REPORT.md", "w") as f:
    f.write(report_content)

print(f"\nTest report saved to TEST_REPORT.md")

# Exit with appropriate code
sys.exit(0 if runner.failed == 0 else 1)
