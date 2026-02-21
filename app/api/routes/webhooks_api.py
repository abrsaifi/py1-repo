"""Webhook management API endpoints"""
from flask import Blueprint, request, jsonify, session
from app.services.webhooks import WebhookManager
from app.utils.logger_enhanced import OperationLogger
from functools import wraps

bp = Blueprint('webhooks', __name__)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/webhooks/register', methods=['POST'])
@login_required
def register_webhook():
    """Register a webhook"""
    op_logger = OperationLogger('webhook-register')
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        event_type = data.get('event_type')
        url = data.get('url')
        secret = data.get('secret')
        
        if not event_type or not url:
            return jsonify({'error': 'event_type and url required'}), 400
        
        op_logger.log_start(user_id=user_id, event_type=event_type)
        
        webhook_id = WebhookManager.register_webhook(user_id, event_type, url, secret)
        
        op_logger.log_success(webhook_id=webhook_id)
        
        return jsonify({
            'success': True,
            'webhook_id': webhook_id,
            'message': 'Webhook registered'
        }), 201
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/webhooks', methods=['GET'])
@login_required
def list_webhooks():
    """List all webhooks for user"""
    try:
        user_id = session.get('user_id')
        webhooks = WebhookManager.get_webhooks(user_id)
        
        return jsonify({
            'success': True,
            'webhooks': [
                {
                    'id': w[0],
                    'event_type': w[1],
                    'url': w[2],
                    'active': w[3],
                    'created_at': w[4]
                }
                for w in webhooks
            ]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/webhooks/<int:webhook_id>', methods=['DELETE'])
@login_required
def delete_webhook(webhook_id):
    """Delete a webhook"""
    op_logger = OperationLogger('webhook-delete')
    try:
        user_id = session.get('user_id')
        
        op_logger.log_start(user_id=user_id, webhook_id=webhook_id)
        
        WebhookManager.delete_webhook(webhook_id, user_id)
        
        op_logger.log_success(webhook_id=webhook_id)
        
        return jsonify({
            'success': True,
            'message': 'Webhook deleted'
        }), 200
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/webhooks/<int:webhook_id>/disable', methods=['POST'])
@login_required
def disable_webhook(webhook_id):
    """Disable a webhook"""
    op_logger = OperationLogger('webhook-disable')
    try:
        user_id = session.get('user_id')
        
        op_logger.log_start(user_id=user_id, webhook_id=webhook_id)
        
        WebhookManager.disable_webhook(webhook_id, user_id)
        
        op_logger.log_success(webhook_id=webhook_id)
        
        return jsonify({
            'success': True,
            'message': 'Webhook disabled'
        }), 200
    
    except Exception as e:
        op_logger.log_error(str(e))
        return jsonify({'error': str(e)}), 500
