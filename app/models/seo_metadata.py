"""SEO metadata model for CMS pages."""
from datetime import datetime
from . import db
from app.utils.datetime_utils import utc_now_naive


class SEOMetadata(db.Model):
    """Per-page SEO metadata and structured data."""
    __tablename__ = 'seo_metadata'

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False, unique=True, index=True)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    keywords = db.Column(db.JSON, default=list)
    canonical_url = db.Column(db.String(500))
    schema_markup = db.Column(db.JSON, default=dict)
    indexable = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    page = db.relationship('Page', back_populates='seo_metadata')

    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'keywords': self.keywords or [],
            'canonical_url': self.canonical_url,
            'schema_markup': self.schema_markup or {},
            'indexable': self.indexable,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
