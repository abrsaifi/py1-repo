#!/usr/bin/env python3
"""Check database schema."""

import sqlite3

conn = sqlite3.connect('docpro_database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users);")

print("\nUSERS TABLE SCHEMA:")
print("="*60)
for row in cursor.fetchall():
    cid, name, type_, notnull, dflt_value, pk = row
    print(f"  {name:20} | {type_:15} | PK={pk} | NOT NULL={notnull}")

conn.close()
