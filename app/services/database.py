"""Database models for persistence layer"""
from datetime import datetime
import sqlite3
import json
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / 'docpro_database.db'

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Conversion history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            operation_type TEXT NOT NULL,
            input_file TEXT,
            output_file TEXT,
            file_size_input INTEGER,
            file_size_output INTEGER,
            duration_ms FLOAT,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_type TEXT NOT NULL,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            total_files_processed INTEGER DEFAULT 0,
            total_data_processed_mb FLOAT DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            data_type TEXT DEFAULT 'string',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

class DatabaseManager:
    """Manage database operations"""
    
    @staticmethod
    def add_conversion_record(operation_type, input_file, status='pending', user_id=None, file_size_input=0):
        """Add conversion record"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversion_history 
            (user_id, operation_type, input_file, file_size_input, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, operation_type, input_file, file_size_input, status, datetime.now()))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    @staticmethod
    def update_conversion_record(record_id, status, output_file=None, file_size_output=0, error_message=None, duration_ms=0):
        """Update conversion record with results"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE conversion_history 
            SET status=?, output_file=?, file_size_output=?, error_message=?, duration_ms=?, completed_at=?
            WHERE id=?
        ''', (status, output_file, file_size_output, error_message, duration_ms, datetime.now(), record_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_history(user_id, limit=50):
        """Get user's conversion history"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM conversion_history 
            WHERE user_id=? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    @staticmethod
    def update_analytics(operation_type, success=True, file_size_mb=0):
        """Update operation analytics"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analytics WHERE operation_type=?', (operation_type,))
        exists = cursor.fetchone()
        
        if exists:
            if success:
                cursor.execute('''
                    UPDATE analytics 
                    SET success_count=success_count+1, total_files_processed=total_files_processed+1,
                        total_data_processed_mb=total_data_processed_mb+?, updated_at=?
                    WHERE operation_type=?
                ''', (file_size_mb, datetime.now(), operation_type))
            else:
                cursor.execute('''
                    UPDATE analytics 
                    SET failure_count=failure_count+1, updated_at=?
                    WHERE operation_type=?
                ''', (datetime.now(), operation_type))
        else:
            if success:
                cursor.execute('''
                    INSERT INTO analytics (operation_type, success_count, total_files_processed, total_data_processed_mb)
                    VALUES (?, 1, 1, ?)
                ''', (operation_type, file_size_mb))
            else:
                cursor.execute('''
                    INSERT INTO analytics (operation_type, failure_count)
                    VALUES (?, 1)
                ''', (operation_type,))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_analytics():
        """Get all analytics"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analytics')
        results = cursor.fetchall()
        conn.close()
        return results
