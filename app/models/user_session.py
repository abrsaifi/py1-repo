"""Persistent user session metadata."""
from datetime import datetime, timezone
import secrets

from . import db
from app.utils.datetime_utils import utc_now_naive


class UserSession(db.Model):
    """Track active and historical user sessions for account management."""
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    device = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False, default='Unknown location')
    ip_address = db.Column(db.String(64), nullable=False, default='Unknown IP')
    is_current = db.Column(db.Boolean, default=False)
    revoked_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    last_active_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    @staticmethod
    def generate_session_token():
        return secrets.token_hex(24)

    @classmethod
    def create_session(cls, user_id, device, location, ip_address, is_current=False):
        return cls(
            user_id=user_id,
            session_token=cls.generate_session_token(),
            device=device,
            location=location,
            ip_address=ip_address,
            is_current=is_current,
        )

    def revoke(self):
        self.revoked_at = datetime.now(timezone.utc)
        self.is_current = False

    def touch(self, is_current=None):
        self.last_active_at = datetime.now(timezone.utc)
        if is_current is not None:
            self.is_current = is_current

    @property
    def is_active(self):
        return self.revoked_at is None

    def to_dict(self):
        return {
            'id': self.id,
            'device': self.device,
            'location': self.location,
            'ip': self.ip_address,
            'last_active': self.last_active_at.isoformat() if self.last_active_at else None,
            'is_current': self.is_current,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
