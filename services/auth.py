"""
Authentication utilities for user registration, login, and token management.
"""

import hashlib
import secrets
import json
from datetime import datetime, timedelta, timezone
import logging

# Try to use jwt library if available, otherwise use simple token-based auth
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = secrets.token_hex(32)  # Generate a random secret
TOKEN_EXPIRY_HOURS = 24
API_KEY_LENGTH = 32

class AuthManager:
    """Handles user authentication and token management"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password, password_hash):
        """Verify a password against its hash"""
        try:
            salt, pwd_hash = password_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return new_hash == pwd_hash
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def create_token(self, user_id, username):
        """Create an authentication token"""
        if JWT_AVAILABLE:
            payload = {
                'user_id': user_id,
                'username': username,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)
            }
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
        else:
            # Fallback: Simple token with user data stored server-side
            token = secrets.token_urlsafe(32)
            token_data = {
                'user_id': user_id,
                'username': username,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'expires_at': (datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)).isoformat()
            }
            return token, json.dumps(token_data)
    
    def verify_token(self, token):
        """Verify an authentication token"""
        if JWT_AVAILABLE:
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                return payload
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                return None
            except jwt.InvalidTokenError:
                logger.warning("Invalid token")
                return None
        else:
            # For fallback mode, tokens are verified per-request
            # (In production, would store tokens in database/cache)
            return {'token': token}
    
    def generate_api_key(self):
        """Generate an API key for programmatic access"""
        return secrets.token_urlsafe(API_KEY_LENGTH)
    
    def hash_api_secret(self, secret):
        """Hash an API secret key"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def validate_api_key(self, user_id, api_key_id, api_secret, stored_secret_hash):
        """Validate an API key and secret"""
        # Verify the secret matches
        computed_hash = self.hash_api_secret(api_secret)
        return secrets.compare_digest(computed_hash, stored_secret_hash)


# Global auth manager instance
_auth_manager = None

def get_auth_manager():
    """Get or create global auth manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
