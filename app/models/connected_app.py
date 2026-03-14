"""Connected third-party application metadata."""
from datetime import datetime

from . import db
from app.utils.datetime_utils import utc_now_naive


class ConnectedApp(db.Model):
    """Store user-managed third-party app connections."""
    __tablename__ = 'connected_apps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    provider = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(16), nullable=False, default='🔗')
    is_connected = db.Column(db.Boolean, default=False)
    last_used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider,
            'name': self.display_name,
            'icon': self.icon,
            'connected': self.is_connected,
            'last_used': self.last_used_at.isoformat() if self.last_used_at else None,
        }
