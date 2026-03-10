"""Webhook system for event delivery and integration."""
from app.models import db
from datetime import datetime, timedelta
from enum import Enum
import json
import hmac
import hashlib
import requests
from functools import wraps
from flask import current_app

class EventType(Enum):
    """Available webhook events."""
    CONVERSION_STARTED = 'conversion.started'
    CONVERSION_COMPLETED = 'conversion.completed'
    CONVERSION_FAILED = 'conversion.failed'
    USER_CREATED = 'user.created'
    USER_DELETED = 'user.deleted'
    SUBSCRIPTION_CREATED = 'subscription.created'
    SUBSCRIPTION_CANCELLED = 'subscription.cancelled'

class WebhookEvent(db.Model):
    """Webhook event model."""
    
    __tablename__ = 'webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_id = db.Column(db.String(255))
    resource_type = db.Column(db.String(50))
    payload = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'resource_type': self.resource_type,
            'payload': self.payload,
            'created_at': self.created_at.isoformat()
        }

class Webhook(db.Model):
    """Webhook subscription model."""
    
    __tablename__ = 'webhooks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    url = db.Column(db.String(2048), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    secret = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True, index=True)
    max_retries = db.Column(db.Integer, default=5)
    retry_delay = db.Column(db.Integer, default=60)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'url': self.url,
            'event_type': self.event_type,
            'active': self.active,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature."""
        expected = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def generate_signature(self, payload):
        """Generate webhook signature."""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

class WebhookDelivery(db.Model):
    """Webhook delivery attempt tracking."""
    
    __tablename__ = 'webhook_deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhooks.id'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('webhook_events.id'), nullable=False, index=True)
    attempt = db.Column(db.Integer, default=1)
    status_code = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    error = db.Column(db.Text)
    delivered_at = db.Column(db.DateTime, index=True)
    next_retry_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'webhook_id': self.webhook_id,
            'event_id': self.event_id,
            'attempt': self.attempt,
            'status_code': self.status_code,
            'error': self.error,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'created_at': self.created_at.isoformat()
        }

class WebhookService:
    """Service for managing webhooks and deliveries."""
    
    @staticmethod
    def create_webhook(user_id, url, event_type, secret):
        """Create webhook subscription."""
        webhook = Webhook(
            user_id=user_id,
            url=url,
            event_type=event_type,
            secret=secret
        )
        db.session.add(webhook)
        db.session.commit()
        return webhook
    
    @staticmethod
    def get_webhooks(user_id, event_type=None, active_only=True):
        """Get user webhooks."""
        query = Webhook.query.filter_by(user_id=user_id)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        if active_only:
            query = query.filter_by(active=True)
        
        return query.all()
    
    @staticmethod
    def delete_webhook(webhook_id, user_id):
        """Delete webhook (soft delete by deactivation)."""
        webhook = Webhook.query.filter_by(id=webhook_id, user_id=user_id).first()
        if webhook:
            webhook.active = False
            db.session.commit()
        return webhook
    
    @staticmethod
    def emit_event(event_type, user_id, resource_id, resource_type, payload):
        """Emit webhook event."""
        # Create event record
        event = WebhookEvent(
            event_type=event_type,
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            payload=payload
        )
        db.session.add(event)
        db.session.commit()
        
        # Get matching webhooks
        webhooks = WebhookService.get_webhooks(user_id, event_type)
        
        # Queue deliveries
        for webhook in webhooks:
            delivery = WebhookDelivery(
                webhook_id=webhook.id,
                event_id=event.id,
                attempt=1
            )
            db.session.add(delivery)
        
        db.session.commit()
        
        # Attempt immediate delivery
        WebhookService.deliver_webhooks(event)
        
        return event
    
    @staticmethod
    def deliver_webhooks(event):
        """Deliver webhook event to subscribers."""
        deliveries = WebhookDelivery.query.filter_by(event_id=event.id).all()
        
        for delivery in deliveries:
            WebhookService.deliver_webhook(delivery)
    
    @staticmethod
    def deliver_webhook(delivery):
        """Deliver single webhook."""
        webhook = Webhook.query.get(delivery.webhook_id)
        event = WebhookEvent.query.get(delivery.event_id)
        
        if not webhook or not event or not webhook.active:
            return False
        
        payload = json.dumps(event.payload)
        signature = webhook.generate_signature(payload)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Event': event.event_type,
            'X-Webhook-ID': str(event.id),
            'X-Webhook-Signature': f"sha256={signature}",
            'X-Webhook-Timestamp': event.created_at.isoformat()
        }
        
        try:
            response = requests.post(
                webhook.url,
                data=payload,
                headers=headers,
                timeout=10
            )
            
            delivery.status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit stored response
            
            if response.status_code in [200, 201, 202, 204]:
                delivery.delivered_at = datetime.utcnow()
                db.session.commit()
                return True
            else:
                # Schedule retry
                WebhookService.schedule_retry(delivery, webhook)
                db.session.commit()
                return False
        
        except requests.RequestException as e:
            delivery.error = str(e)[:500]
            WebhookService.schedule_retry(delivery, webhook)
            db.session.commit()
            return False
    
    @staticmethod
    def schedule_retry(delivery, webhook):
        """Schedule webhook retry."""
        if delivery.attempt < webhook.max_retries:
            delivery.attempt += 1
            delivery.next_retry_at = datetime.utcnow() + timedelta(
                seconds=webhook.retry_delay * (2 ** (delivery.attempt - 1))  # Exponential backoff
            )
        else:
            # Max retries reached
            delivery.error = "Max retries exceeded"
    
    @staticmethod
    def retry_pending_deliveries():
        """Retry pending webhook deliveries (run as scheduled task)."""
        pending = WebhookDelivery.query.filter(
            (WebhookDelivery.delivered_at == None) &
            ((WebhookDelivery.next_retry_at == None) | (WebhookDelivery.next_retry_at <= datetime.utcnow()))
        ).all()
        
        for delivery in pending:
            WebhookService.deliver_webhook(delivery)
        
        return len(pending)

def emit_webhook_event(event_type):
    """Decorator to emit webhook events after function execution."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Extract event data from result (should be dict with user_id, resource_id, resource_type, payload)
            if isinstance(result, dict) and 'emit_webhook' in result and result['emit_webhook']:
                WebhookService.emit_event(
                    event_type=event_type,
                    user_id=result['user_id'],
                    resource_id=result.get('resource_id'),
                    resource_type=result.get('resource_type'),
                    payload=result.get('payload', {})
                )
            
            return result
        
        return decorated_function
    return decorator
