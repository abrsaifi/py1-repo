"""User model."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import enum
from app.utils.datetime_utils import utc_now_naive

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class User(db.Model):
    """User account model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    
    # Plan and quota
    plan = db.Column(db.String(50), default='free')  # free, pro, enterprise
    quota_gb = db.Column(db.Integer, default=5)  # Storage quota in GB
    used_gb = db.Column(db.Float, default=0.0)  # Used storage in GB
    
    # Role and permissions
    role = db.Column(db.String(50), default='user')  # user, admin, moderator
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    analytics_opt_in = db.Column(db.Boolean, default=True)
    marketing_opt_in = db.Column(db.Boolean, default=True)
    personalization_opt_in = db.Column(db.Boolean, default=True)
    deletion_requested_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    conversions = db.relationship('Conversion', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    api_keys = db.relationship('APIKey', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    subscription = db.relationship('Subscription', backref='user', uselist=False, cascade='all, delete-orphan')
    invoices = db.relationship('BillingInvoice', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    billing_profile = db.relationship('BillingProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    connected_apps = db.relationship('ConnectedApp', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def get_remaining_quota(self):
        """Get remaining storage quota in GB."""
        return max(0, self.quota_gb - self.used_gb)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'plan': self.plan,
            'quota_gb': self.quota_gb,
            'used_gb': self.used_gb,
            'remaining_quota_gb': self.get_remaining_quota(),
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'two_factor_enabled': self.two_factor_enabled,
            'analytics_opt_in': self.analytics_opt_in,
            'marketing_opt_in': self.marketing_opt_in,
            'personalization_opt_in': self.personalization_opt_in,
            'deletion_requested_at': self.deletion_requested_at.isoformat() if self.deletion_requested_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
    
    def __repr__(self):
        return f'<User {self.email}>'
