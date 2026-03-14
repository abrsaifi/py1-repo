#!/usr/bin/env python3
"""
Reset Subscriber Credentials - Create/Update demo subscriber account

Demo Credentials:
  Username: subscriber
  Password: demo123
  Role: subscriber (user with subscription)
  Email: subscriber@example.com
"""

import sqlite3
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.auth import AuthManager
from app.services.database import init_db, DB_PATH

def reset_subscriber_credentials():
    """Reset subscriber credentials in database"""
    
    print("=" * 70)
    print("SUBSCRIBER CREDENTIALS RESET")
    print("=" * 70)
    
    # Demo credentials
    SUBSCRIBER_USERNAME = 'subscriber'
    SUBSCRIBER_EMAIL = 'subscriber@example.com'
    SUBSCRIBER_PASSWORD = 'demo123'
    
    try:
        # Ensure database exists and is initialized
        print("\n📦 Initializing database...")
        init_db()
        print("✓ Database initialized")
        
        # Connect to database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if subscriber already exists
        cursor.execute('SELECT id FROM users WHERE username=?', (SUBSCRIBER_USERNAME,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing subscriber user
            print(f"\n🔄 Updating existing subscriber user...")
            subscriber_id = existing[0]
            password_hash = AuthManager.hash_password(SUBSCRIBER_PASSWORD)
            api_key = AuthManager.generate_api_key()
            
            cursor.execute('''
                UPDATE users 
                SET password_hash=?, api_key=?, is_active=1, role='subscriber'
                WHERE id=?
            ''', (password_hash, api_key, subscriber_id))
            
            conn.commit()
            print(f"✓ Subscriber user updated (ID: {subscriber_id})")
        else:
            # Create new subscriber user
            print(f"\n📝 Creating new subscriber user...")
            success, user_id, api_key = AuthManager.create_user(
                SUBSCRIBER_USERNAME,
                SUBSCRIBER_EMAIL,
                SUBSCRIBER_PASSWORD
            )
            
            if success:
                cursor.execute("UPDATE users SET role='subscriber' WHERE id=?", (user_id,))
                conn.commit()
                print(f"✓ Subscriber user created (ID: {user_id})")
            else:
                print("✗ Failed to create subscriber user")
                return False
        
        conn.close()
        
        # Display credentials
        print("\n" + "=" * 70)
        print("✅ SUBSCRIBER ACCOUNT READY")
        print("=" * 70)
        print(f"\n📧 Email:    {SUBSCRIBER_EMAIL}")
        print(f"👤 Username: {SUBSCRIBER_USERNAME}")
        print(f"🔐 Password: {SUBSCRIBER_PASSWORD}")
        print(f"\n🌐 Login at: http://localhost:5173")
        print(f"   • Click 'User Login'")
        print(f"   • Enter credentials above")
        print(f"   • User Dashboard will load")
        print("\n" + "=" * 70)
        print("\n💡 Quick Demo Login:")
        print("   • Frontend fallback: username=subscriber, password=demo123")
        print("   • Works even if backend is unavailable")
        print("\n" + "=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = reset_subscriber_credentials()
    sys.exit(0 if success else 1)
