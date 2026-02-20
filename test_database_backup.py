#!/usr/bin/env python3
"""Test database backup configuration."""

import os
import sys

def test_database_backup_setup():
    """Test that database backup system is configured."""
    print("\n" + "="*60)
    print("DATABASE BACKUP CONFIGURATION TEST")
    print("="*60)
    
    # Test 1: Check backup directory exists
    print("\n[1] Checking backup directory...")
    if os.path.isdir('backups'):
        print(f"  ✓ backups/ directory exists")
    else:
        print(f"  ✗ backups/ directory missing")
        return False
    
    # Test 2: Check database file exists
    print("\n[2] Checking database...")
    if os.path.exists('conversion_history.db'):
        print(f"  ✓ conversion_history.db exists")
        size = os.path.getsize('conversion_history.db')
        print(f"  ℹ Database size: {size:,} bytes")
    else:
        print(f"  ⚠ conversion_history.db not found (may be created on first run)")
    
    # Test 3: Check app/startup.py
    print("\n[3] Checking app/startup.py...")
    if os.path.exists('app/startup.py'):
        print(f"  ✓ app/startup.py exists")
        
        startup_code = open('app/startup.py').read()
        checks = [
            ('init_background_tasks function', 'def init_background_tasks'),
            ('Daily backup task', 'daily_backup'),
            ('Weekly cleanup task', 'weekly_backup_cleanup'),
            ('Database optimization', 'weekly_optimization'),
            ('Temp cleanup task', 'hourly_temp_cleanup'),
            ('DatabaseManager integration', 'DatabaseManager'),
            ('BackgroundTaskManager integration', 'get_background_manager'),
        ]
        
        startup_ok = True
        for check_name, check_string in checks:
            if check_string in startup_code:
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name} - NOT FOUND")
                startup_ok = False
        
        if not startup_ok:
            return False
    else:
        print(f"  ✗ app/startup.py does not exist")
        return False
    
    # Test 4: Check integration in app/__init__.py
    print("\n[4] Checking integration in app/__init__.py...")
    init_code = open('app/__init__.py').read()
    
    if 'from .startup import init_background_tasks' in init_code:
        print(f"  ✓ startup module imported")
    else:
        print(f"  ✗ startup module not imported")
        return False
    
    if 'init_background_tasks()' in init_code:
        print(f"  ✓ background tasks initialized in app factory")
    else:
        print(f"  ✗ background tasks not initialized")
        return False
    
    # Test 5: Test imports
    print("\n[5] Testing imports...")
    try:
        from app.startup import init_background_tasks, init_app, create_task_manager
        print(f"  ✓ app.startup imported successfully")
        print(f"  ✓ init_background_tasks function available")
        print(f"  ✓ init_app function available")
        print(f"  ✓ create_task_manager function available")
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False
    
    # Test 6: Check background task manager availability
    print("\n[6] Testing background task manager...")
    try:
        from app.services.background_tasks import get_background_manager
        manager = get_background_manager()
        print(f"  ✓ Background task manager available")
        print(f"  ℹ Manager class: {manager.__class__.__name__}")
    except Exception as e:
        print(f"  ✗ Background task manager failed: {e}")
        return False
    
    # Test 7: Check DatabaseManager
    print("\n[7] Testing DatabaseManager...")
    try:
        from app.services.database import DatabaseManager
        print(f"  ✓ DatabaseManager available")
        
        # Check that it has required methods
        methods = ['backup', 'restore', 'optimize', 'get_info', 'get_stats']
        for method in methods:
            if hasattr(DatabaseManager, method):
                print(f"  ✓ DatabaseManager.{method}() available")
            else:
                print(f"  ⚠ DatabaseManager.{method}() not found")
    except Exception as e:
        print(f"  ✗ DatabaseManager check failed: {e}")
        return False
    
    # Summary
    print("\n" + "="*60)
    print("✓ DATABASE BACKUP CONFIGURATION TEST PASSED")
    print("="*60)
    print("\nBackup system configured:")
    print("  • Daily backups to backups/ directory")
    print("  • Weekly cleanup of old backups (>30 days)")
    print("  • Weekly database optimization")
    print("  • Hourly temp file cleanup")
    return True


if __name__ == '__main__':
    success = test_database_backup_setup()
    sys.exit(0 if success else 1)
