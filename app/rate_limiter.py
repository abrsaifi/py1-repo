"""Advanced tiered rate limiting system."""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
from datetime import datetime, timedelta
from app.models import db, APIKey, Subscription
import time

class RateLimitConfig:
    """Rate limit configuration by user tier."""
    
    TIERS = {
        'free': {
            'requests_per_minute': 10,
            'requests_per_hour': 100,
            'requests_per_day': 500,
            'concurrent_conversions': 1,
            'file_size_limit_mb': 10,
            'storage_limit_gb': 1
        },
        'pro': {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000,
            'concurrent_conversions': 5,
            'file_size_limit_mb': 100,
            'storage_limit_gb': 50
        },
        'enterprise': {
            'requests_per_minute': 500,
            'requests_per_hour': 10000,
            'requests_per_day': None,  # Unlimited
            'concurrent_conversions': 50,
            'file_size_limit_mb': 500,
            'storage_limit_gb': 1000
        }
    }
    
    @staticmethod
    def get_tier_limits(plan_type):
        """Get rate limits for subscription plan."""
        return RateLimitConfig.TIERS.get(plan_type, RateLimitConfig.TIERS['free'])

class RateLimitTracker(db.Model):
    """Track rate limit usage."""
    
    __tablename__ = 'rate_limit_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_key.id'), index=True)
    endpoint = db.Column(db.String(255), index=True)
    request_count = db.Column(db.Integer, default=0)
    window_start = db.Column(db.DateTime, default=datetime.utcnow)
    window_type = db.Column(db.String(10))  # 'minute', 'hour', 'day'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'endpoint': self.endpoint,
            'request_count': self.request_count,
            'window_type': self.window_type,
            'window_start': self.window_start.isoformat()
        }

class AdvancedRateLimiter:
    """Advanced tiered rate limiting."""
    
    @staticmethod
    def check_rate_limit(user_id=None, api_key=None, endpoint=None):
        """Check if request should be allowed."""
        if user_id:
            return AdvancedRateLimiter._check_user_rate_limit(user_id, endpoint)
        elif api_key:
            return AdvancedRateLimiter._check_api_key_rate_limit(api_key, endpoint)
        return True
    
    @staticmethod
    def _check_user_rate_limit(user_id, endpoint):
        """Check rate limit for authenticated user."""
        from app.models import User
        
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Get user's subscription plan
        subscription = db.session.query(Subscription).filter_by(user_id=user_id).first()
        plan = subscription.plan_type if subscription else 'free'
        
        limits = RateLimitConfig.get_tier_limits(plan)
        
        # Check minute limit
        minute_tracker = RateLimitTracker.query.filter(
            RateLimitTracker.user_id == user_id,
            RateLimitTracker.endpoint == endpoint,
            RateLimitTracker.window_type == 'minute',
            RateLimitTracker.window_start >= datetime.utcnow() - timedelta(minutes=1)
        ).first()
        
        if minute_tracker and minute_tracker.request_count >= limits['requests_per_minute']:
            return False, "Rate limit exceeded: Too many requests per minute"
        
        # Check hour limit
        hour_tracker = RateLimitTracker.query.filter(
            RateLimitTracker.user_id == user_id,
            RateLimitTracker.endpoint == endpoint,
            RateLimitTracker.window_type == 'hour',
            RateLimitTracker.window_start >= datetime.utcnow() - timedelta(hours=1)
        ).first()
        
        if hour_tracker and hour_tracker.request_count >= limits['requests_per_hour']:
            return False, "Rate limit exceeded: Too many requests per hour"
        
        # Check day limit
        if limits['requests_per_day']:
            day_tracker = RateLimitTracker.query.filter(
                RateLimitTracker.user_id == user_id,
                RateLimitTracker.endpoint == endpoint,
                RateLimitTracker.window_type == 'day',
                RateLimitTracker.window_start >= datetime.utcnow() - timedelta(days=1)
            ).first()
            
            if day_tracker and day_tracker.request_count >= limits['requests_per_day']:
                return False, "Rate limit exceeded: Too many requests per day"
        
        return True, "OK"
    
    @staticmethod
    def _check_api_key_rate_limit(api_key, endpoint):
        """Check rate limit for API key."""
        key_record = APIKey.query.filter_by(key=api_key).first()
        if not key_record or not key_record.is_active():
            return False, "Invalid or expired API key"
        
        return AdvancedRateLimiter._check_user_rate_limit(key_record.user_id, endpoint)
    
    @staticmethod
    def record_request(user_id=None, api_key_id=None, endpoint=None):
        """Record request for rate limiting."""
        window_start = datetime.utcnow()
        
        # Record minute window
        minute_tracker = RateLimitTracker(
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            window_type='minute',
            window_start=window_start,
            request_count=1
        )
        db.session.add(minute_tracker)
        
        # Record hour window
        hour_tracker = RateLimitTracker(
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            window_type='hour',
            window_start=window_start,
            request_count=1
        )
        db.session.add(hour_tracker)
        
        # Record day window
        day_tracker = RateLimitTracker(
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            window_type='day',
            window_start=window_start,
            request_count=1
        )
        db.session.add(day_tracker)
        
        db.session.commit()
    
    @staticmethod
    def get_usage_stats(user_id, endpoint):
        """Get current rate limit usage."""
        minute = RateLimitTracker.query.filter(
            RateLimitTracker.user_id == user_id,
            RateLimitTracker.endpoint == endpoint,
            RateLimitTracker.window_type == 'minute',
            RateLimitTracker.window_start >= datetime.utcnow() - timedelta(minutes=1)
        ).first()
        
        hour = RateLimitTracker.query.filter(
            RateLimitTracker.user_id == user_id,
            RateLimitTracker.endpoint == endpoint,
            RateLimitTracker.window_type == 'hour',
            RateLimitTracker.window_start >= datetime.utcnow() - timedelta(hours=1)
        ).first()
        
        day = RateLimitTracker.query.filter(
            RateLimitTracker.user_id == user_id,
            RateLimitTracker.endpoint == endpoint,
            RateLimitTracker.window_type == 'day',
            RateLimitTracker.window_start >= datetime.utcnow() - timedelta(days=1)
        ).first()
        
        return {
            'minute': minute.request_count if minute else 0,
            'hour': hour.request_count if hour else 0,
            'day': day.request_count if day else 0
        }

def tiered_rate_limit(endpoint_name):
    """Decorator for tiered rate limiting based on subscription plan."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            from app.middleware.auth import get_current_user
            
            user = get_current_user()
            if not user:
                return f(*args, **kwargs)
            
            allowed, message = AdvancedRateLimiter.check_rate_limit(
                user_id=user.id,
                endpoint=endpoint_name
            )
            
            if not allowed:
                return jsonify({'error': message}), 429
            
            AdvancedRateLimiter.record_request(user_id=user.id, endpoint=endpoint_name)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def cleanup_old_rate_limit_records(days=30):
    """Clean up old rate limit tracking records (run as scheduled task)."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted = RateLimitTracker.query.filter(
        RateLimitTracker.created_at < cutoff
    ).delete()
    db.session.commit()
    return deleted
