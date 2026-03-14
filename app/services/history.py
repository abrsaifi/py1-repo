import os
import sqlite3
import json
from datetime import datetime, timezone
import threading


def init_history_db(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    operation TEXT,
                    files TEXT,
                    status TEXT,
                    message TEXT
                )
            ''')
            conn.commit()
    except Exception:
        pass


def log_history(db_path, operation, files, status='success', message=''):
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO history (timestamp, operation, files, status, message) VALUES (?, ?, ?, ?, ?)',
                      (datetime.now(timezone.utc).isoformat(), operation, json.dumps(files), status, message))
            conn.commit()
    except Exception:
        pass


def start_background_tasks(db_path):
    # For now just ensure DB exists; additional background tasks can be added here
    try:
        init_history_db(db_path)
    except Exception:
        pass
