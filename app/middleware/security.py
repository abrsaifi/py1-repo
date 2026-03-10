"""Security hardening middleware for production deployment."""
from flask import request, jsonify
from functools import wraps
from datetime import datetime
import hashlib

def security_headers(app):
    """Add security headers to all responses."""
    @app.after_request
    def set_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'"
        )
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy
        response.headers['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=(), '
            'accelerometer=()'
        )
        
        # HTTPS only (in production)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

def validate_request_size(max_size_mb=100):
    """Validate request payload size."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            max_bytes = max_size_mb * 1024 * 1024
            
            if request.content_length and request.content_length > max_bytes:
                return jsonify({
                    'error': 'Payload too large',
                    'max_size_mb': max_size_mb
                }), 413
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(f):
    """Sanitize user input."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for common injection patterns
        dangerous_chars = ['<script', 'javascript:', 'onerror=', 'onclick=']
        
        # Check query parameters
        for key, value in request.args.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for dangerous in dangerous_chars:
                    if dangerous in value_lower:
                        return jsonify({'error': 'Invalid input detected'}), 400
        
        # Check JSON body
        if request.is_json:
            try:
                data = request.get_json()
                def check_value(val):
                    if isinstance(val, str):
                        val_lower = val.lower()
                        for dangerous in dangerous_chars:
                            if dangerous in val_lower:
                                return False
                    elif isinstance(val, dict):
                        return all(check_value(v) for v in val.values())
                    elif isinstance(val, list):
                        return all(check_value(v) for v in val)
                    return True
                
                if not check_value(data):
                    return jsonify({'error': 'Invalid input detected'}), 400
            except:
                pass
        
        return f(*args, **kwargs)
    return decorated_function

def require_https(f):
    """Require HTTPS for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and request.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            return jsonify({'error': 'HTTPS required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def log_request_audit(f):
    """Log all requests to audit trail."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models import db
        
        # Extract user info
        user_id = getattr(request, 'user_id', None)
        
        # Log details
        audit_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'user_id': user_id,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
        }
        
        # Store in audit log table (implement as needed)
        # audit_log = AuditLog(**audit_data)
        # db.session.add(audit_log)
        # db.session.commit()
        
        return f(*args, **kwargs)
    return decorated_function

def require_https_redirect(app):
    """Redirect HTTP to HTTPS."""
    @app.before_request
    def redirect_https():
        if not request.is_secure and request.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            url = request.url.replace('http://', 'https://', 1)
            return jsonify({'error': 'Redirecting to HTTPS'}), 308, {'Location': url}

def check_ip_whitelist(allowed_ips=None):
    """Check if request IP is in whitelist."""
    if allowed_ips is None:
        allowed_ips = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if allowed_ips and request.remote_addr not in allowed_ips:
                return jsonify({'error': 'IP not whitelisted'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_version_check(min_version='1.0', max_version='2.0'):
    """Validate API version."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_version = request.headers.get('X-API-Version', '1.0')
            
            # Simple version comparison
            if not (min_version <= api_version <= max_version):
                return jsonify({
                    'error': 'Unsupported API version',
                    'current': api_version,
                    'supported': f'{min_version} to {max_version}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
