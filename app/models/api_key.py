"""API Key model for programmatic access."""
from datetime import datetime, timedelta
from . import db
import secrets

class APIKey(db.Model):
    """User API keys for programmatic access."""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Key details
    name = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    key_preview = db.Column(db.String(20), nullable=False)  # Show last 4 chars: "sk_...abc1"
    
    # Permissions/Scope
    scopes = db.Column(db.JSON, default=['conversions:read', 'conversions:write'])
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_deprecated = db.Column(db.Boolean, default=False)
    
    # Usage tracking
    last_used_at = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    # Expiration
    expires_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def generate_key():
        """Generate a secure API key."""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    @classmethod
    def create_key(cls, user_id, name, scopes=None, expires_in_days=None):
        """Create a new API key for a user."""
        key = cls.generate_key()
        key_preview = f"sk_...{key[-4:]}"
        
        api_key = cls(
            user_id=user_id,
            name=name,
            key=key,
            key_preview=key_preview,
            scopes=scopes or ['conversions:read', 'conversions:write'],
        )
        
        if expires_in_days:
            api_key.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        return api_key
    
    def is_expired(self):
        """Check if API key is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def is_valid(self):
        """Check if API key is valid and usable."""
        return self.is_active and not self.is_deprecated and not self.is_expired()
    
    def has_scope(self, scope):
        """Check if key has a specific scope."""
        return scope in self.scopes
    
    def record_usage(self):
        """Record that this key was used."""
        self.last_used_at = datetime.utcnow()
        self.usage_count += 1
    
    def to_dict(self, include_full_key=False):
        """Convert to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'key_preview': self.key_preview,
            'scopes': self.scopes,
            'is_active': self.is_active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'usage_count': self.usage_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        # Only include full key if explicitly requested (e.g., during creation)
        if include_full_key:
            data['key'] = self.key
        
        return data
    
    def __repr__(self):
        return f'<APIKey {self.id}: {self.name} ({self.key_preview})>'
