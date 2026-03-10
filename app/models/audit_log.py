"""Audit log model for tracking data access and changes."""
from app import db
from .base import Base

class DataAccessLog(Base):
    """Log of data access events."""
    __tablename__ = 'data_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50))
    resource = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        })
        return data
