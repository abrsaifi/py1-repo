"""Subscription model."""
from datetime import datetime, timedelta
from . import db
import enum

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Subscription(db.Model):
    """User subscription information."""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Plan details
    plan = db.Column(db.String(50), default='free')  # free, pro, enterprise
    storage_quota_gb = db.Column(db.Integer, default=5)
    monthly_conversion_limit = db.Column(db.Integer, default=100)
    max_file_size_mb = db.Column(db.Integer, default=50)
    
    # Billing
    price_per_month = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Dates
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_period_start = db.Column(db.DateTime, default=datetime.utcnow)
    current_period_end = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    renewal_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    cancelled_at = db.Column(db.DateTime)
    
    # Usage tracking (current month)
    conversions_used_this_month = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_trial(self):
        """Check if subscription is in trial period."""
        # Free plans are essentially trial/basic plans
        return self.plan == 'free'
    
    def is_expired(self):
        """Check if subscription has expired."""
        if not self.is_active:
            return True
        return datetime.utcnow() > self.current_period_end
    
    def days_until_renewal(self):
        """Get days until renewal."""
        if self.is_expired():
            return 0
        delta = self.renewal_date - datetime.utcnow()
        return max(0, delta.days)
    
    def can_convert(self):
        """Check if user can perform conversions."""
        if not self.is_active or self.is_expired():
            return False
        if self.conversions_used_this_month >= self.monthly_conversion_limit:
            return False
        return True
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan,
            'storage_quota_gb': self.storage_quota_gb,
            'monthly_conversion_limit': self.monthly_conversion_limit,
            'max_file_size_mb': self.max_file_size_mb,
            'price_per_month': self.price_per_month,
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'days_until_renewal': self.days_until_renewal(),
            'conversions_used_this_month': self.conversions_used_this_month,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
        }
    
    def __repr__(self):
        return f'<Subscription {self.user_id}: {self.plan}>'
