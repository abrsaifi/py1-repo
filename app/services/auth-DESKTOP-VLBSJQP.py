"""Authentication and API key management"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'docpro_database.db'

class AuthManager:
    """Manage user authentication and API keys"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using PBKDF2"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify password against hash"""
        try:
            salt, pwd_hash = password_hash.split('$')
            pwd_hash_computed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return pwd_hash_computed.hex() == pwd_hash
        except:
            return False
    
    @staticmethod
    def create_user(username, email, password):
        """Create new user"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            password_hash = AuthManager.hash_password(password)
            api_key = AuthManager.generate_api_key()
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, api_key)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, api_key))
            
            conn.commit()
            user_id = cursor.lastrowid
            return True, user_id, api_key
        except sqlite3.IntegrityError:
            return False, None, None
        finally:
            conn.close()
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user by username and password"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username=?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, password_hash = result
            if AuthManager.verify_password(password, password_hash):
                return True, user_id
        
        return False, None
    
    @staticmethod
    def verify_api_key(api_key):
        """Verify API key and return user_id"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM users 
            WHERE api_key=? AND is_active=1
        ''', (api_key,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    @staticmethod
    def generate_api_key():
        """Generate new API key"""
        return 'dpk_' + secrets.token_urlsafe(32)
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user info by ID"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, api_key, created_at, is_active
            FROM users WHERE id=?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result    
    @staticmethod
    def reset_api_key(user_id):
        """Reset user's API key"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        try:
            new_key = AuthManager.generate_api_key()
            cursor.execute('''
                UPDATE users SET api_key=? WHERE id=?
            ''', (new_key, user_id))
            
            conn.commit()
            return new_key
        finally:
            conn.close()
def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    from flask import request, jsonify
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'Missing API key'}), 401
        
        user_id = AuthManager.verify_api_key(api_key)
        if not user_id:
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401
        
        # Pass user_id to the function
        return f(user_id=user_id, *args, **kwargs)
    
    return decorated_function
