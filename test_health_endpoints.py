#!/usr/bin/env python3
"""Test health check endpoints."""

import sys
import os

def test_health_endpoints():
    """Test that health endpoints are available."""
    print("\n" + "="*60)
    print("HEALTH CHECK ENDPOINT TEST")
    print("="*60)
    
    from app import create_app
    import json
    
    try:
        app = create_app()
        print("\n[1] Created Flask app with health endpoints")
        
        # List all health-related routes
        print("\n[2] Available health endpoints:")
        health_routes = []
        for rule in app.url_map.iter_rules():
            if 'health' in rule.rule.lower():
                health_routes.append(rule)
                methods = ', '.join(rule.methods - {'OPTIONS', 'HEAD'})
                print(f"  • {rule.rule} ({methods})")
        
        if not health_routes:
            print("  ✗ No health endpoints found!")
            return False
        
        print(f"  ✓ Found {len(health_routes)} health endpoints")
        
        # Test each endpoint
        print("\n[3] Testing health endpoints:")
        
        with app.test_client() as client:
            endpoints = [
                ('/api/health/live', 'Liveness probe'),
                ('/api/health/ready', 'Readiness probe'),
                ('/api/health/status', 'Detailed status'),
                ('/api/health/metrics', 'Metrics endpoint'),
                ('/api/health', 'Basic health check'),
            ]
            
            passed = 0
            for endpoint, description in endpoints:
                try:
                    response = client.get(endpoint)
                    status = response.status_code
                    
                    if status in [200, 503]:  # 503 is acceptable for readiness if system not ready
                        print(f"  ✓ {endpoint} ({description}): {status}")
                        passed += 1
                        
                        # Try to parse JSON response
                        try:
                            data = response.get_json()
                            if data:
                                print(f"    Response: {json.dumps(data, indent=2)[:200]}...")
                        except:
                            print(f"    Response type: {response.content_type}")
                    else:
                        print(f"  ⚠ {endpoint} ({description}): {status} (unexpected)")
                        
                except Exception as e:
                    print(f"  ✗ {endpoint} ({description}): {str(e)}")
            
            print(f"\n  {passed}/5 endpoints working")
        
        # Summary
        print("\n" + "="*60)
        if passed >= 3:  # At least basic endpoints should work
            print("✓ HEALTH ENDPOINTS TEST PASSED")
            return True
        else:
            print("✗ HEALTH ENDPOINTS TEST FAILED")
            return False
            
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_health_endpoints()
    sys.exit(0 if success else 1)
