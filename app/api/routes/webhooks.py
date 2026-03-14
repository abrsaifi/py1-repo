"""Webhook management API routes for Phase 3."""
from flask import Blueprint, request, jsonify
from app.middleware.auth import auth_required
from app.webhook_service import WebhookService, Webhook, WebhookEvent, WebhookDelivery
from app.models import db
import secrets
from datetime import datetime, timezone

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@webhooks_bp.route('', methods=['POST'])
@auth_required
def create_webhook():
    """Create webhook subscription."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    data = request.get_json()
    
    # Validate input
    if not data or 'url' not in data or 'event_type' not in data:
        return jsonify({'error': 'url and event_type are required'}), 400
    
    url = data.get('url')
    event_type = data.get('event_type')
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'url must be http or https'}), 400
    
    # Validate event type
    valid_events = [
        'conversion.started', 'conversion.completed', 'conversion.failed',
        'user.created', 'user.deleted',
        'subscription.created', 'subscription.cancelled'
    ]
    
    if event_type not in valid_events:
        return jsonify({'error': f'Invalid event_type. Valid types: {", ".join(valid_events)}'}), 400
    
    # Generate secret for webhook
    secret = secrets.token_urlsafe(32)
    
    webhook = WebhookService.create_webhook(
        user_id=user.id,
        url=url,
        event_type=event_type,
        secret=secret
    )
    
    return jsonify({
        **webhook.to_dict(),
        'secret': secret  # Only return secret on creation
    }), 201

@webhooks_bp.route('/<int:webhook_id>', methods=['GET'])
@auth_required
def get_webhook(webhook_id):
    """Get webhook details."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=user.id).first()
    
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    return jsonify(webhook.to_dict()), 200

@webhooks_bp.route('', methods=['GET'])
@auth_required
def list_webhooks():
    """List user webhooks."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    event_type = request.args.get('event_type')
    active_only = request.args.get('active_only', default='true').lower() == 'true'
    
    webhooks = WebhookService.get_webhooks(
        user.id,
        event_type=event_type,
        active_only=active_only
    )
    
    return jsonify({
        'count': len(webhooks),
        'webhooks': [w.to_dict() for w in webhooks]
    }), 200

@webhooks_bp.route('/<int:webhook_id>', methods=['PUT'])
@auth_required
def update_webhook(webhook_id):
    """Update webhook."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=user.id).first()
    
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    data = request.get_json()
    
    if 'url' in data:
        if not data['url'].startswith(('http://', 'https://')):
            return jsonify({'error': 'url must be http or https'}), 400
        webhook.url = data['url']
    
    if 'active' in data:
        webhook.active = bool(data['active'])
    
    if 'max_retries' in data:
        webhook.max_retries = int(data['max_retries'])
    
    if 'retry_delay' in data:
        webhook.retry_delay = int(data['retry_delay'])
    
    db.session.commit()
    
    return jsonify(webhook.to_dict()), 200

@webhooks_bp.route('/<int:webhook_id>', methods=['DELETE'])
@auth_required
def delete_webhook(webhook_id):
    """Delete webhook."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    webhook = WebhookService.delete_webhook(webhook_id, user.id)
    
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    return jsonify({'message': 'Webhook deleted'}), 200

@webhooks_bp.route('/events', methods=['GET'])
@auth_required
def list_webhook_events():
    """List webhook events for user."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=20, type=int)
    event_type = request.args.get('event_type')
    
    query = WebhookEvent.query.filter_by(user_id=user.id)
    
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    paginated = query.order_by(WebhookEvent.created_at.desc()).paginate(
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages,
        'events': [e.to_dict() for e in paginated.items]
    }), 200

@webhooks_bp.route('/events/<int:event_id>', methods=['GET'])
@auth_required
def get_webhook_event(event_id):
    """Get webhook event details."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    event = WebhookEvent.query.filter_by(id=event_id, user_id=user.id).first()
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Get delivery attempts
    deliveries = WebhookDelivery.query.filter_by(event_id=event_id).all()
    
    return jsonify({
        **event.to_dict(),
        'deliveries': [d.to_dict() for d in deliveries]
    }), 200

@webhooks_bp.route('/events/<int:event_id>/deliveries', methods=['GET'])
@auth_required
def get_event_deliveries(event_id):
    """Get delivery attempts for event."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    
    # Verify user owns the event
    event = WebhookEvent.query.filter_by(id=event_id, user_id=user.id).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    deliveries = WebhookDelivery.query.filter_by(event_id=event_id).all()
    
    return jsonify({
        'event_id': event_id,
        'total_deliveries': len(deliveries),
        'deliveries': [d.to_dict() for d in deliveries]
    }), 200

@webhooks_bp.route('/test/<int:webhook_id>', methods=['POST'])
@auth_required
def test_webhook(webhook_id):
    """Send test webhook event."""
    from app.middleware.auth import get_current_user
    
    user = get_current_user()
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=user.id).first()
    
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Create test event
    test_payload = {
        'event_type': 'test',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'message': 'This is a test webhook event'
    }
    
    # Emit test event
    from app.webhook_service import WebhookService
    event = WebhookService.emit_event(
        event_type='test',
        user_id=user.id,
        resource_id='test',
        resource_type='test',
        payload=test_payload
    )
    
    return jsonify({
        'event_id': event.id,
        'message': 'Test webhook sent',
        'event': event.to_dict()
    }), 200
