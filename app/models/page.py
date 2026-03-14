"""CMS page model."""
from datetime import datetime
from . import db
from app.utils.datetime_utils import utc_now_naive


class Page(db.Model):
    """Database-backed CMS page definition."""
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    page_type = db.Column(db.String(50), default='landing', nullable=False)
    status = db.Column(db.String(50), default='draft', nullable=False, index=True)
    content = db.Column(db.JSON, default=dict)
    custom_css = db.Column(db.Text)
    is_homepage = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    widgets = db.relationship(
        'Widget',
        back_populates='page',
        order_by='Widget.position',
        cascade='all, delete-orphan',
        lazy='select'
    )
    seo_metadata = db.relationship(
        'SEOMetadata',
        back_populates='page',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='select'
    )

    def to_dict(self, include_widgets=True, include_seo=True):
        payload = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'page_type': self.page_type,
            'status': self.status,
            'content': self.content or {},
            'custom_css': self.custom_css,
            'is_homepage': self.is_homepage,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_widgets:
            payload['widgets'] = [widget.to_dict() for widget in self.widgets]
        if include_seo:
            payload['seo_metadata'] = self.seo_metadata.to_dict() if self.seo_metadata else None
        return payload
