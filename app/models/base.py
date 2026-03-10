"""Base model class for all database models."""
from app import db

class Base(db.Model):
    """Base model with common fields."""
    __abstract__ = True
    
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': getattr(self, 'id', None),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
