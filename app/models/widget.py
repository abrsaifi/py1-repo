"""CMS widget model."""
from datetime import datetime
from . import db
from app.utils.datetime_utils import utc_now_naive


class Widget(db.Model):
    """Reusable page widget stored in the database."""
    __tablename__ = 'widgets'

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    widget_type = db.Column(db.String(100), nullable=False, index=True)
    position = db.Column(db.Integer, default=0, nullable=False)
    config = db.Column(db.JSON, default=dict)
    is_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    page = db.relationship('Page', back_populates='widgets')

    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'name': self.name,
            'widget_type': self.widget_type,
            'position': self.position,
            'config': self.config or {},
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
