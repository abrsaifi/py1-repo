#!/usr/bin/env python3
"""Test Step 2 integration - error handlers and logging."""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules import correctly."""
    print("\n[TEST 1] Testing imports...")
    try:
        from app.utils.errors import register_error_handlers, AppError, ConversionError
        print("  ✓ Error handlers imported")
    except Exception as e:
        print(f"  ✗ Error handler import failed: {e}")
        raise AssertionError(f"Error handler import failed: {e}") from e
    
    try:
        from app.utils.logger_setup import LoggerSetup
        print("  ✓ Logger setup imported")
    except Exception as e:
        print(f"  ✗ Logger setup import failed: {e}")
        raise AssertionError(f"Logger setup import failed: {e}") from e


def test_logging_setup():
    """Test logging initialization."""
    print("\n[TEST 2] Testing logging setup...")
    try:
        from app.utils.logger_setup import LoggerSetup
        import logging
        
        logger = LoggerSetup.setup(
            app_name='test_docpro',
            level='INFO',
            log_file='logs/test_app.log',
            use_json=False
        )
        
        logger.info("Test log message")
        print(f"  ✓ Logger created and configured")
        print(f"  ✓ Logger name: {logger.name}")
        print(f"  ✓ Logger level: {logging.getLevelName(logger.level)}")
        
        # Check that log file exists
        if os.path.exists('logs/test_app.log'):
            print(f"  ✓ Log file created at logs/test_app.log")
        else:
            print(f"  ⚠ Log file not yet created (normal if not written)")
    except Exception as e:
        print(f"  ✗ Logging setup failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"Logging setup failed: {e}") from e


def test_error_handlers():
    """Test error handler registration."""
    print("\n[TEST 3] Testing error handler registration...")
    try:
        from flask import Flask
        from app.utils.errors import register_error_handlers, ConversionError
        
        app = Flask(__name__)
        register_error_handlers(app)
        
        # Check that error handlers are registered
        if app.error_handler_spec:
            print(f"  ✓ Error handlers registered with Flask")
            print(f"  ✓ Number of error handler specs: {len(app.error_handler_spec)}")
        else:
            print(f"  ⚠ No error handlers found (might be registered globally)")
    except Exception as e:
        print(f"  ✗ Error handler registration failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"Error handler registration failed: {e}") from e


def test_server_initialization():
    """Test server.py initialization."""
    print("\n[TEST 4] Testing server.py integration...")
    try:
        from server import app, logger
        
        print(f"  ✓ Server app imported")
        print(f"  ✓ Logger available: {bool(logger)}")
        print(f"  ✓ Secret key configured: {bool(app.secret_key)}")
        
        # Check error handlers
        if app.error_handler_spec:
            print(f"  ✓ Error handlers registered: {len(app.error_handler_spec)} specs")
    except Exception as e:
        print(f"  ✗ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"Server initialization failed: {e}") from e


def test_app_factory():
    """Test app/__init__.py factory."""
    print("\n[TEST 5] Testing app factory (create_app)...")
    try:
        from app import create_app
        
        app = create_app()
        print(f"  ✓ App factory successful")
        print(f"  ✓ App name: {app.name}")
        print(f"  ✓ Logger available: {bool(app.logger)}")
        
        # Check error handlers
        if app.error_handler_spec:
            print(f"  ✓ Error handlers registered: {len(app.error_handler_spec)} specs")
    except Exception as e:
        print(f"  ✗ App factory failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"App factory failed: {e}") from e


def test_health_endpoint():
    """Test health endpoint availability."""
    print("\n[TEST 6] Testing health endpoint...")
    try:
        from app import create_app
        
        app = create_app()
        
        # Check if health blueprint is registered
        with app.app_context():
            # Try to find health routes
            found_health = False
            for rule in app.url_map.iter_rules():
                if 'health' in rule.rule:
                    found_health = True
                    print(f"  ✓ Found route: {rule.rule} ({rule.methods})")
            
            if found_health:
                print(f"  ✓ Health endpoints are registered")
            else:
                print(f"  ⚠ No health endpoints found")
    except Exception as e:
        print(f"  ✗ Health endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"Health endpoint test failed: {e}") from e


def main():
    """Run all tests."""
    print("="*60)
    print("Step 2 Integration Tests")
    print("="*60)
    
    test_cases = [
        ('imports', test_imports),
        ('logging', test_logging_setup),
        ('errors', test_error_handlers),
        ('server', test_server_initialization),
        ('factory', test_app_factory),
        ('health', test_health_endpoint),
    ]
    results = {}
    for name, test_func in test_cases:
        try:
            test_func()
            results[name] = True
        except AssertionError:
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All Step 2 integration tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
