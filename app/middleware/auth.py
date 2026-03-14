"""Authentication and authorization middleware."""
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timezone
import os


def _extract_bearer_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None

    parts = auth_header.split(' ', 1)
    if len(parts) != 2 or parts[0].lower() != 'bearer' or not parts[1].strip():
        return None

    return parts[1].strip()


def _coerce_user_id(user_id):
    if isinstance(user_id, str) and user_id.isdigit():
        return int(user_id)
    return user_id

def auth_required(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = _extract_bearer_token()
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        try:
            # Import here to avoid circular imports
            from flask_jwt_extended import decode_token
            
            payload = decode_token(token)
            request.user_id = _coerce_user_id(payload.get('sub'))
            request.current_user = payload
            
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token', 'details': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = _extract_bearer_token()
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        try:
            from flask_jwt_extended import decode_token
            from app.models import User
            
            payload = decode_token(token)
            user_id = _coerce_user_id(payload.get('sub'))
            
            # Fetch user to check role
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
            
            request.user_id = user_id
            request.current_user = user
            
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'details': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def api_key_required(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = None
        
        # Check for API key in header or query parameter
        if 'X-API-Key' in request.headers:
            api_key = request.headers['X-API-Key']
        elif 'api_key' in request.args:
            api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'Missing API key'}), 401
        
        try:
            from app.models import APIKey
            
            key_obj = APIKey.query.filter_by(key=api_key).first()
            
            if not key_obj or not key_obj.is_valid():
                return jsonify({'error': 'Invalid or expired API key'}), 401
            
            # Record usage
            key_obj.record_usage()
            from app.models import db
            db.session.commit()
            
            request.user_id = key_obj.user_id
            request.api_key = key_obj
            
        except Exception as e:
            return jsonify({'error': 'API key validation failed', 'details': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(max_requests=100, time_window=3600):
    """Decorator to rate limit requests (simple in-memory implementation)."""
    from collections import defaultdict, deque
    
    request_history = defaultdict(deque)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address or user_id as the key
            if hasattr(request, 'user_id'):
                key = f"user_{request.user_id}"
            else:
                key = f"ip_{request.remote_addr}"
            
            now = datetime.now(timezone.utc).timestamp()
            
            # Remove old requests outside the time window
            while request_history[key] and request_history[key][0] < now - time_window:
                request_history[key].popleft()
            
            # Check if limit exceeded
            if len(request_history[key]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    f'limit': max_requests,
                    'time_window_seconds': time_window
                }), 429
            
            # Record this request
            request_history[key].append(now)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def require_scope(*required_scopes):
    """Decorator to check if API key has required scopes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'api_key'):
                return jsonify({'error': 'This endpoint requires API key authentication'}), 401
            
            api_key = request.api_key
            
            for scope in required_scopes:
                if not api_key.has_scope(scope):
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_scopes': list(required_scopes),
                        'available_scopes': api_key.scopes
                    }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator
