#!/usr/bin/env python3
"""
Reset admin and subscriber credentials script.
This script removes existing demo users and creates new ones with fresh credentials.
Uses raw SQL to work with the current database schema.
"""

import sqlite3
import secrets
import hashlib
import sys
from pathlib import Path
from datetime import datetime


def hash_password(password):
    """Hash password using PBKDF2 (matching AuthManager format)."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def generate_secure_password(length=16):
    """Generate a secure random password."""
    return secrets.token_urlsafe(length)


def reset_credentials():
    """Reset admin and subscriber credentials."""
    project_root = Path(__file__).parent
    db_path = project_root / 'docpro_database.db'
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("RESETTING ADMIN AND SUBSCRIBER CREDENTIALS")
    print("="*60 + "\n")
    
    try:
        # Delete existing users
        print("Deleting existing admin and subscriber users...")
        cursor.execute("DELETE FROM users WHERE username IN ('admin', 'subscriber')")
        conn.commit()
        print("[OK] Existing users deleted\n")
        
        # Generate new passwords
        admin_password = generate_secure_password()
        subscriber_password = generate_secure_password()
        
        # Hash passwords (using AuthManager's format)
        admin_hash = hash_password(admin_password)
        subscriber_hash = hash_password(subscriber_password)
        
        # Get current timestamp
        now = datetime.utcnow().isoformat()
        
        # Create new admin user
        print("Creating new admin user...")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, created_at, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, ('admin', 'admin@docpro.local', admin_hash, now, 1))
        conn.commit()
        print("[OK] New admin user created\n")
        
        # Create new subscriber user
        print("Creating new subscriber user...")
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, created_at, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, ('subscriber', 'subscriber@docpro.local', subscriber_hash, now, 1))
        conn.commit()
        print("[OK] New subscriber user created\n")
        
        # Print new credentials
        print("="*60)
        print("NEW CREDENTIALS CREATED SUCCESSFULLY")
        print("="*60 + "\n")
        
        print("ADMIN USER")
        print("-" * 60)
        print(f"  Email:    admin@docpro.local")
        print(f"  Username: admin")
        print(f"  Password: {admin_password}\n")
        
        print("SUBSCRIBER USER")
        print("-" * 60)
        print(f"  Email:    subscriber@docpro.local")
        print(f"  Username: subscriber")
        print(f"  Password: {subscriber_password}\n")
        
        print("="*60)
        print("WARNING: SAVE THESE CREDENTIALS IN A SECURE LOCATION")
        print("="*60 + "\n")
        
        # Save to file
        credentials_file = project_root / 'CREDENTIALS.txt'
        with open(credentials_file, 'w') as f:
            f.write("DOCPRO - NEW CREDENTIALS\n")
            f.write("="*60 + "\n")
            f.write(f"Created: {now}\n\n")
            f.write("ADMIN USER\n")
            f.write("-"*60 + "\n")
            f.write(f"Email:    admin@docpro.local\n")
            f.write(f"Username: admin\n")
            f.write(f"Password: {admin_password}\n\n")
            f.write("SUBSCRIBER USER\n")
            f.write("-"*60 + "\n")
            f.write(f"Email:    subscriber@docpro.local\n")
            f.write(f"Username: subscriber\n")
            f.write(f"Password: {subscriber_password}\n")
        
        print(f"[OK] Credentials saved to: {credentials_file}\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        cursor.close()
        conn.close()
        sys.exit(1)


if __name__ == '__main__':
    reset_credentials()

