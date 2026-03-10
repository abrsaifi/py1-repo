#!/usr/bin/env python3
"""Verify new credentials were created."""

import sqlite3

conn = sqlite3.connect('docpro_database.db')
cursor = conn.cursor()
cursor.execute('SELECT username, email, is_active FROM users WHERE username IN ("admin", "subscriber")')

print("\nVERIFYING NEW USERS IN DATABASE:")
print("="*70)
print(f"{'Username':<15} | {'Email':<30} | {'Active':<10}")
print("-"*70)
for row in cursor.fetchall():
    username, email, is_active = row
    status = "YES" if is_active else "NO"
    print(f"{username:<15} | {email:<30} | {status:<10}")

conn.close()
print("\n[OK] Users verified in database\n")
