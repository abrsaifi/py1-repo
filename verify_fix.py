#!/usr/bin/env python3
"""
Verification script - Confirms the Multi-Region API fix is correctly applied.
Run this anytime to verify the fix is in place and working.
"""

import sys
sys.path.insert(0, r'c:\Users\dell\OneDrive\Documents\py1')

print("\n" + "="*70)
print("MULTI-REGION API FIX VERIFICATION SCRIPT")
print("="*70 + "\n")

def test_step(step_num, description, test_func):
    """Run a test step and report results."""
    try:
        print(f"[Step {step_num}] {description}...", end=" ")
        result = test_func()
        if result:
            print("[PASS]")
            return True
        else:
            print("[FAIL]")
            return False
    except Exception as e:
        print(f"[FAIL]: {str(e)}")
        return False

# Test 1: Flask app creation
def test_app_creation():
    from app import create_app
    app = create_app()
    return app is not None

# Test 2: Multi-region routes
def test_routes():
    from app import create_app
    app = create_app()
    routes = [rule for rule in app.url_map.iter_rules() if 'multi-region' in str(rule.rule)]
    return len(routes) == 21

# Test 3: Model imports
def test_models():
    from app.models.multi_region import RegionConfig, RegionReplica
    return True

# Test 4: Relationship configuration
def test_relationship():
    from app import create_app
    from app.models.multi_region import RegionConfig
    from sqlalchemy import inspect
    
    app = create_app()
    with app.app_context():
        mapper = inspect(RegionConfig)
        relationships = {rel.key: rel for rel in mapper.relationships}
        return 'replicas' in relationships

# Test 5: Check source code
def test_source_code():
    with open(r'c:\Users\dell\OneDrive\Documents\py1\app\models\multi_region.py', 'r') as f:
        content = f.read()
        return "foreign_keys='RegionReplica.primary_region_id'" in content

# Run tests
results = []
results.append(test_step(1, "Creating Flask app", test_app_creation))
results.append(test_step(2, "Verifying 21 multi-region routes", test_routes))
results.append(test_step(3, "Loading RegionConfig and RegionReplica models", test_models))
results.append(test_step(4, "Checking relationship configuration", test_relationship))
results.append(test_step(5, "Verifying source code contains fix", test_source_code))

# Summary
print("\n" + "-"*70)
passed = sum(results)
total = len(results)
print(f"\nTEST SUMMARY: {passed}/{total} TESTS PASSED")

if passed == total:
    print("\n[OK] ALL VERIFICATION TESTS PASSED")
    print("\n[STATUS] Multi-Region API Fix is correctly applied and working!")
    print("[READY] System is ready for testing and deployment")
    print("="*70 + "\n")
    sys.exit(0)
else:
    print(f"\n[ERROR] {total - passed} TEST(S) FAILED")
    print("\n[ERROR] Fix verification failed - please review the changes")
    print("="*70 + "\n")
    sys.exit(1)
