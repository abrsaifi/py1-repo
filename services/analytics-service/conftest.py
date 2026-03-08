"""
Pytest configuration and shared fixtures for analytics service tests
"""

import pytest
import os
from datetime import datetime, timedelta


@pytest.fixture(scope="session")
def test_config():
    """Session-wide test configuration"""
    return {
        'testing': True,
        'database_url': os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:'),
        'redis_url': os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/1'),
    }


@pytest.fixture(scope="function")
def cleanup_after_test():
    """Cleanup fixture after each test"""
    yield
    # Cleanup code here if needed


@pytest.fixture
def mock_jwt_token():
    """Generate mock JWT token for testing"""
    # In real scenario, this would be a valid JWT token
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJ0ZXN0LXRlbmFudCIsInVzZXJfaWQiOiJ0ZXN0LXVzZXIiLCJpYXQiOjE2NzcxMjM0NTYsImV4cCI6MTY3NzEyNzA1Nn0.X1Z2Y3W4U5T6S7R8P9Q0'


@pytest.fixture
def sample_metric_data():
    """Sample metric data for testing"""
    return {
        'tenant_id': 'test-tenant-001',
        'service_name': 'test-service',
        'metric_name': 'test_metric',
        'metric_type': 'gauge',
        'aggregation_level': 'hour',
        'timestamp': datetime.utcnow(),
        'period_start': datetime.utcnow() - timedelta(hours=1),
        'period_end': datetime.utcnow(),
        'value': 50.0,
        'min_value': 40.0,
        'max_value': 60.0,
    }


@pytest.fixture
def sample_service_metric():
    """Sample service metric data"""
    return {
        'tenant_id': 'test-tenant-001',
        'service_name': 'test-service',
        'period_start': datetime.utcnow() - timedelta(hours=1),
        'period_end': datetime.utcnow(),
        'response_time_p50': 100.0,
        'response_time_p95': 250.0,
        'response_time_p99': 500.0,
        'response_time_avg': 150.0,
        'total_requests': 10000,
        'successful_requests': 9980,
        'failed_requests': 20,
        'error_rate': 0.2,
        'uptime_percent': 99.95,
    }


@pytest.fixture
def sample_alert_data():
    """Sample alert data"""
    return {
        'tenant_id': 'test-tenant-001',
        'metric_name': 'error_rate',
        'condition_type': 'threshold',
        'threshold_value': 5.0,
        'comparison_operator': '>',
        'severity': 'critical',
        'is_active': True,
        'notification_channels': ['email', 'slack'],
    }


@pytest.fixture
def sample_dashboard_data():
    """Sample dashboard data"""
    return {
        'tenant_id': 'test-tenant-001',
        'name': 'Executive Dashboard',
        'description': 'High-level business metrics',
        'dashboard_type': 'executive',
        'widgets': [
            {
                'id': 'widget-1',
                'type': 'metric',
                'title': 'Revenue',
                'config': {'metric': 'revenue'}
            },
            {
                'id': 'widget-2',
                'type': 'chart',
                'title': 'Growth Trend',
                'config': {'metric': 'growth_rate', 'period': '30'}
            }
        ]
    }


@pytest.fixture
def sample_report_data():
    """Sample report data"""
    return {
        'tenant_id': 'test-tenant-001',
        'name': 'Monthly Performance Report',
        'report_type': 'summary',
        'schedule': 'monthly',
        'recipients': ['admin@example.com'],
        'format': 'pdf',
    }


@pytest.fixture
def pagination_params():
    """Test pagination parameters"""
    return {
        'page': 1,
        'per_page': 50,
        'sort_by': 'created_at',
        'sort_order': 'desc',
    }


@pytest.fixture
def time_range_params():
    """Test time range parameters"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    return {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'granularity': 'hour',
    }


@pytest.fixture
def filter_params():
    """Test filter parameters"""
    return {
        'tenant_id': 'test-tenant-001',
        'service_name': 'test-service',
        'metric_name': 'test_metric',
        'aggregation_level': 'hour',
    }


def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Mark all tests by default as unit tests
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)
