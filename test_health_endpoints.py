#!/usr/bin/env python3
"""Test health check endpoints."""

import json
import sys

from app import create_app


def _run_health_endpoint_checks(verbose=False):
    app = create_app()

    health_routes = []
    for rule in app.url_map.iter_rules():
        if 'health' in rule.rule.lower():
            health_routes.append(rule)
            if verbose:
                methods = ', '.join(rule.methods - {'OPTIONS', 'HEAD'})
                print(f"  - {rule.rule} ({methods})")

    results = []
    with app.test_client() as client:
        endpoints = [
            ('/api/health/live', 'Liveness probe'),
            ('/api/health/ready', 'Readiness probe'),
            ('/api/health/status', 'Detailed status'),
            ('/api/health/metrics', 'Metrics endpoint'),
            ('/api/health', 'Basic health check'),
        ]

        for endpoint, description in endpoints:
            response = client.get(endpoint)
            data = response.get_json(silent=True)
            results.append({
                'endpoint': endpoint,
                'description': description,
                'status_code': response.status_code,
                'json': data,
                'content_type': response.content_type,
            })

            if verbose:
                print(f"  - {endpoint} ({description}): {response.status_code}")
                if data:
                    print(f"    {json.dumps(data, indent=2)[:200]}...")

    passed = sum(1 for result in results if result['status_code'] in {200, 503})
    return {
        'health_routes': health_routes,
        'results': results,
        'passed': passed,
    }


def test_health_endpoints():
    """Test that health endpoints are available."""
    summary = _run_health_endpoint_checks(verbose=False)

    assert summary['health_routes'], 'No health endpoints found'
    assert summary['passed'] >= 3, (
        f"Expected at least 3 working health endpoints, got {summary['passed']}"
    )


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print('HEALTH CHECK ENDPOINT TEST')
    print("=" * 60)

    try:
        summary = _run_health_endpoint_checks(verbose=True)
        success = bool(summary['health_routes']) and summary['passed'] >= 3
        print(f"\n{summary['passed']}/5 endpoints working")
        print("\n" + "=" * 60)
        print('✓ HEALTH ENDPOINTS TEST PASSED' if success else '✗ HEALTH ENDPOINTS TEST FAILED')
        sys.exit(0 if success else 1)
    except Exception as exc:
        print(f"\n✗ Test failed: {exc}")
        raise
