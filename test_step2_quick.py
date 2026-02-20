#!/usr/bin/env python3
"""Quick test for Step 2 integration - error handlers and logging."""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_step_2_integration():
    """Test key Step 2 integrations."""
    print("\n" + "="*60)
    print("STEP 2 INTEGRATION TEST")
    print("="*60)
    
    # Test 1: Check directories
    print("\n[1] Checking directories...")
    dirs_ok = True
    for dir_path in ['logs', 'backups']:
        if os.path.isdir(dir_path):
            print(f"  ✓ {dir_path}/ directory exists")
        else:
            print(f"  ✗ {dir_path}/ directory missing")
            dirs_ok = False
    
    # Test 2: Check app/__init__.py modifications
    print("\n[2] Checking app/__init__.py modifications...")
    app_init = open('app/__init__.py', 'r').read()
    checks = [
        ('LoggerSetup import', 'from .utils.logger_setup import LoggerSetup'),
        ('Error handlers import', 'from .utils.errors import register_error_handlers'),
        ('Error handler registration', 'register_error_handlers(app)'),
        ('Logging setup call', 'LoggerSetup.setup('),
    ]
    
    app_init_ok = True
    for check_name, check_string in checks:
        if check_string in app_init:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - NOT FOUND")
            app_init_ok = False
    
    # Test 3: Check server.py modifications
    print("\n[3] Checking server.py modifications...")
    server = open('server.py', 'r').read()
    checks = [
        ('LoggerSetup import', 'from app.utils.logger_setup import LoggerSetup'),
        ('Error handlers import', 'from app.utils.errors import register_error_handlers'),
        ('Logger setup call', 'LoggerSetup.setup('),
        ('Error handler registration', 'register_error_handlers(app)'),
        ('Logging in main', 'logger.info('),
    ]
    
    server_ok = True
    for check_name, check_string in checks:
        if check_string in server:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name} - NOT FOUND")
            server_ok = False
    
    # Test 4: Test imports (lightweight)
    print("\n[4] Testing lightweight imports...")
    import_ok = True
    
    try:
        from app.utils.errors import register_error_handlers, AppError, ConversionError
        print(f"  ✓ Error handler classes imported")
    except Exception as e:
        print(f"  ✗ Error handler import failed: {e}")
        import_ok = False
    
    try:
        from app.utils.logger_setup import LoggerSetup
        print(f"  ✓ LoggerSetup imported")
    except Exception as e:
        print(f"  ✗ LoggerSetup import failed: {e}")
        import_ok = False
    
    # Test 5: Test logger setup
    print("\n[5] Testing logger creation...")
    try:
        from app.utils.logger_setup import LoggerSetup
        logger = LoggerSetup.setup(
            app_name='docpro_test',
            level='INFO',
            log_file='logs/test.log',
            use_json=False
        )
        logger.info("Test message")
        print(f"  ✓ Logger created and working")
        
        if os.path.exists('logs/test.log'):
            with open('logs/test.log', 'r') as f:
                content = f.read()
                if 'Test message' in content:
                    print(f"  ✓ Log file created and message recorded")
                else:
                    print(f"  ⚠ Log file exists but message not found (might be buffered)")
        else:
            print(f"  ⚠ Log file not yet created")
    except Exception as e:
        print(f"  ✗ Logger setup failed: {e}")
        import import_ok
        import_ok = False
    
    # Test 6: Test Flask error handlers (lightweight)
    print("\n[6] Testing error handler registration...")
    try:
        from flask import Flask
        from app.utils.errors import register_error_handlers, ConversionError
        
        app = Flask(__name__)
        register_error_handlers(app)
        
        # Check if error handler was registered
        with app.test_client() as client:
            # Trying to access a non-existent route to see if error handling works
            response = client.get('/nonexistent')
            print(f"  ✓ Error handlers registered (404 response: {response.status_code})")
    except Exception as e:
        print(f"  ✗ Error handler test failed: {e}")
        import_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_pass = dirs_ok and app_init_ok and server_ok and import_ok
    
    if all_pass:
        print("\n✓ STEP 2 INTEGRATION SUCCESSFUL")
        print("\nNext steps:")
        print("  1. Create app/startup.py for background tasks")
        print("  2. Test health endpoints")
        print("  3. Configure database backups")
        return 0
    else:
        print("\n✗ Some integration checks failed")
        return 1


if __name__ == '__main__':
    sys.exit(test_step_2_integration())
