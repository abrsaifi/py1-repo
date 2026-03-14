"""Authentication API routes"""
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, session
from app.services.auth import AuthManager
from app.models import UserSession, db
from app.utils.logger_enhanced import AuditLogger, OperationLogger
from functools import wraps

try:
    from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
except ImportError:  # pragma: no cover - optional dependency in some environments
    create_access_token = None
    get_jwt_identity = None
    verify_jwt_in_request = None

bp = Blueprint('auth', __name__)


def _describe_device(user_agent):
    ua = (user_agent or '').lower()
    browser = 'Browser'
    platform = 'Desktop'

    if 'edg' in ua:
        browser = 'Edge'
    elif 'chrome' in ua:
        browser = 'Chrome'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'

    if 'iphone' in ua:
        platform = 'iPhone'
    elif 'android' in ua:
        platform = 'Android'
    elif 'mac os' in ua or 'macintosh' in ua:
        platform = 'Mac'
    elif 'windows' in ua:
        platform = 'Windows'
    elif 'linux' in ua:
        platform = 'Linux'

    return f'{browser} on {platform}'


def _track_login_session(user_id):
    active_sessions = UserSession.query.filter_by(user_id=user_id).filter(UserSession.revoked_at.is_(None)).all()
    for item in active_sessions:
        item.is_current = False

    session_record = UserSession.create_session(
        user_id=user_id,
        device=_describe_device(request.headers.get('User-Agent', '')),
        location=request.headers.get('X-Forwarded-For', request.remote_addr or 'Unknown location'),
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr or 'Unknown IP'),
        is_current=True,
    )
    db.session.add(session_record)
    db.session.commit()


def _revoke_latest_session(user_id):
    session_record = UserSession.query.filter_by(user_id=user_id).filter(UserSession.revoked_at.is_(None)).order_by(UserSession.last_active_at.desc()).first()
    if session_record:
        session_record.revoked_at = datetime.now(timezone.utc)
        session_record.is_current = False
        db.session.commit()


def _coerce_user_id(user_id):
    if isinstance(user_id, str) and user_id.isdigit():
        return int(user_id)
    return user_id


def _build_access_token(user_id, username, email, role):
    if not create_access_token:
        return None

    additional_claims = {
        'role': role or 'user',
        'username': username,
        'email': email,
        'is_admin': (role or 'user') == 'admin'
    }
    return create_access_token(identity=str(user_id), additional_claims=additional_claims)


def _get_authenticated_user_id():
    user_id = session.get('user_id')
    if user_id:
        return user_id

    if verify_jwt_in_request and get_jwt_identity:
        try:
            verify_jwt_in_request(optional=True)
            jwt_identity = get_jwt_identity()
            if jwt_identity:
                return _coerce_user_id(jwt_identity)
        except Exception:
            return None

    return None

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not _get_authenticated_user_id():
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

        access_token = _build_access_token(user_id, username, email, 'user')
        
        return jsonify({
            'success': True,
            'token': access_token,
            'user_id': user_id,
            'api_key': api_key,
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'role': 'user',
                'name': username
            },
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
        user_row = AuthManager.get_user_by_id(user_id)
        api_key = user_row[3] if user_row else None
        user_role = user_row[6] if user_row and len(user_row) > 6 else 'user'
        email = user_row[2] if user_row else ''
        access_token = _build_access_token(user_id, username, email, user_role)
        
        op_logger.log_success(user_id=user_id)
        AuditLogger.log_action(user_id, 'login', 'auth', 'success')
        _track_login_session(user_id)
        
        return jsonify({
            'success': True,
            'token': access_token,
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'role': user_role,
                'name': username
            },
            'user_id': user_id,
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
        _revoke_latest_session(user_id)
    
    # Clear the session
    session.clear()
    
    return jsonify({'success': True, 'message': 'Logout successful'}), 200

@bp.route('/auth/me', methods=['GET'])
def me():
    """Get current user info - supports both session and Bearer token"""
    user_id = _get_authenticated_user_id()

    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
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
    user_id = _get_authenticated_user_id()
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
