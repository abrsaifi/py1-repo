"""Authentication API routes"""
from flask import Blueprint, request, jsonify, session
from app.services.auth import AuthManager
from app.utils.logger_enhanced import AuditLogger, OperationLogger
from functools import wraps

bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/auth/register', methods=['POST'])
def register():
    """Register new user"""
    op_logger = OperationLogger('register')
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        op_logger.log_start(username=username, email=email)
        success, user_id, api_key = AuthManager.create_user(username, email, password)
        
        if not success:
            op_logger.log_error('User already exists')
            AuditLogger.log_action(username, 'register', 'user', 'failed')
            return jsonify({'error': 'Username or email already exists'}), 400
        
        op_logger.log_success(user_id=user_id)
        AuditLogger.log_action(user_id, 'register', 'user', 'success')
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'api_key': api_key,
            'message': 'Registration successful'
        }), 201
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    op_logger = OperationLogger('login')
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        op_logger.log_start(username=username)
        success, user_id = AuthManager.authenticate_user(username, password)
        
        if not success:
            op_logger.log_error('Invalid credentials')
            AuditLogger.log_action(username, 'login', 'auth', 'failed')
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Store in session
        session['user_id'] = user_id
        session['username'] = username
        
        # Get user info
        user = AuthManager.get_user_by_id(user_id)
        api_key = user[4] if user else None
        
        op_logger.log_success(user_id=user_id)
        AuditLogger.log_action(user_id, 'login', 'auth', 'success')
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'username': username,
            'api_key': api_key,
            'message': 'Login successful'
        }), 200
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/logout', methods=['POST'])
def logout():
    """Logout user - clears session and logs the action"""
    user_id = session.get('user_id')
    
    # If no session, try to get user_id from Bearer token (for compatibility)
    if not user_id:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # Could verify token and extract user_id here if needed
            # For now, just accept the logout request
            pass
    
    # Log the action if we have a user_id
    if user_id:
        AuditLogger.log_action(user_id, 'logout', 'auth', 'success')
    
    # Clear the session
    session.clear()
    
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@bp.route('/auth/me', methods=['GET'])
@login_required
def me():
    """Get current user info"""
    user_id = session.get('user_id')
    user = AuthManager.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': user[0],
        'username': user[1],
        'email': user[2],
        'api_key': user[3],
        'created_at': user[4],
        'is_active': user[5]
    }), 200

@bp.route('/auth/reset-api-key', methods=['POST'])
@login_required
def reset_api_key():
    """Reset user API key"""
    user_id = session.get('user_id')
    op_logger = OperationLogger('reset-api-key')
    
    try:
        op_logger.log_start(user_id=user_id)
        new_key = AuthManager.reset_api_key(user_id)
        
        op_logger.log_success(new_key=new_key)
        AuditLogger.log_action(user_id, 'reset-api-key', 'auth', 'success')
        
        return jsonify({
            'success': True,
            'api_key': new_key,
            'message': 'API key reset successfully'
        }), 200
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/auth/verify-api-key/<api_key>', methods=['GET'])
def verify_api_key(api_key):
    """Verify API key"""
    user_id = AuthManager.verify_api_key(api_key)
    
    if not user_id:
        return jsonify({'valid': False}), 401
    
    return jsonify({'valid': True, 'user_id': user_id}), 200
