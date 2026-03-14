#!/usr/bin/env python3
"""
Reset Admin Credentials - Create/Update demo admin account

Demo Credentials:
  Username: admin
  Password: demo123
  Role: admin
  Email: admin@example.com
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.auth import AuthManager
from app.services.database import init_db, DB_PATH

def reset_admin_credentials():
    """Reset admin credentials in database"""
    
    print("=" * 70)
    print("ADMIN CREDENTIALS RESET")
    print("=" * 70)
    
    # Demo credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'demo123'
    
    try:
        # Ensure database exists and is initialized
        print("\n📦 Initializing database...")
        init_db()
        print("✓ Database initialized")
        
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if admin already exists
        cursor.execute('SELECT id FROM users WHERE username=?', (ADMIN_USERNAME,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing admin user
            print(f"\n🔄 Updating existing admin user...")
            admin_id = existing[0]
            password_hash = AuthManager.hash_password(ADMIN_PASSWORD)
            api_key = AuthManager.generate_api_key()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash=?, api_key=?, is_active=1, role='admin'
                WHERE id=?
            ''', (password_hash, api_key, admin_id))
            
            conn.commit()
            print(f"✓ Admin user updated (ID: {admin_id})")
        else:
            # Create new admin user
            print(f"\n📝 Creating new admin user...")
            success, user_id, api_key = AuthManager.create_user(
                ADMIN_USERNAME,
                ADMIN_EMAIL,
                ADMIN_PASSWORD
            )
            
            if success:
                cursor.execute("UPDATE users SET role='admin' WHERE id=?", (user_id,))
                conn.commit()
                print(f"✓ Admin user created (ID: {user_id})")
            else:
                print("✗ Failed to create admin user")
                return False
        
        conn.close()
        
        # Display credentials
        print("\n" + "=" * 70)
        print("✅ ADMIN ACCOUNT READY")
        print("=" * 70)
        print(f"\n📧 Email:    {ADMIN_EMAIL}")
        print(f"👤 Username: {ADMIN_USERNAME}")
        print(f"🔐 Password: {ADMIN_PASSWORD}")
        print(f"\n🌐 Login at: http://localhost:5173")
        print(f"   • Click 'Admin Login'")
        print(f"   • Enter credentials above")
        print(f"   • Dashboard will load automatically")
        print("\n" + "=" * 70)
        print("\n💡 Quick Demo Login:")
        print("   • Frontend fallback: username=admin, password=demo123")
        print("   • Works even if backend is unavailable")
        print("\n" + "=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = reset_admin_credentials()
    sys.exit(0 if success else 1)
