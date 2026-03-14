"""CMS service layer."""
from datetime import datetime, timezone
import re

from app.models import db, Page, Widget, SEOMetadata


def _slugify(value):
    value = (value or '').strip().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'page'


class CMSService:
    """CRUD helpers for CMS pages and widgets."""

    @staticmethod
    def list_pages(include_drafts=True):
        query = Page.query.order_by(Page.updated_at.desc())
        if not include_drafts:
            query = query.filter_by(status='published')
        return query.all()

    @staticmethod
    def get_page(page_id):
        return Page.query.get(page_id)

    @staticmethod
    def get_page_by_slug(slug, include_drafts=False):
        query = Page.query.filter_by(slug=slug)
        if not include_drafts:
            query = query.filter_by(status='published')
        return query.first()

    @staticmethod
    def create_page(data):
        title = (data.get('title') or '').strip()
        if not title:
            raise ValueError('title is required')

        slug = _slugify(data.get('slug') or title)
        if Page.query.filter_by(slug=slug).first():
            raise ValueError('slug already exists')

        page = Page(
            title=title,
            slug=slug,
            description=data.get('description'),
            page_type=data.get('page_type') or 'landing',
            status=data.get('status') or 'draft',
            content=data.get('content') or {},
            custom_css=data.get('custom_css'),
            is_homepage=bool(data.get('is_homepage', False)),
            published_at=datetime.now(timezone.utc) if (data.get('status') == 'published') else None,
        )
        db.session.add(page)
        db.session.flush()

        CMSService._upsert_seo_metadata(page, data.get('seo_metadata') or {})
        CMSService._replace_widgets(page, data.get('widgets') or [])

        db.session.commit()
        return page

    @staticmethod
    def update_page(page, data):
        title = (data.get('title') or page.title or '').strip()
        if not title:
            raise ValueError('title is required')

        new_slug = _slugify(data.get('slug') or page.slug or title)
        existing = Page.query.filter(Page.slug == new_slug, Page.id != page.id).first()
        if existing:
            raise ValueError('slug already exists')

        page.title = title
        page.slug = new_slug
        page.description = data.get('description', page.description)
        page.page_type = data.get('page_type', page.page_type)
        page.status = data.get('status', page.status)
        page.content = data.get('content', page.content)
        page.custom_css = data.get('custom_css', page.custom_css)
        page.is_homepage = bool(data.get('is_homepage', page.is_homepage))
        if page.status == 'published' and not page.published_at:
            page.published_at = datetime.now(timezone.utc)

        if 'seo_metadata' in data:
            CMSService._upsert_seo_metadata(page, data.get('seo_metadata') or {})
        if 'widgets' in data:
            CMSService._replace_widgets(page, data.get('widgets') or [])

        db.session.commit()
        return page

    @staticmethod
    def delete_page(page):
        db.session.delete(page)
        db.session.commit()

    @staticmethod
    def _replace_widgets(page, widgets):
        Widget.query.filter_by(page_id=page.id).delete()
        for index, widget in enumerate(widgets):
            db.session.add(Widget(
                page_id=page.id,
                name=(widget.get('name') or widget.get('widget_type') or f'widget-{index + 1}'),
                widget_type=widget.get('widget_type') or widget.get('type') or 'text',
                position=widget.get('position', index),
                config=widget.get('config') or {},
                is_enabled=widget.get('is_enabled', True),
            ))

    @staticmethod
    def _upsert_seo_metadata(page, seo_data):
        seo = page.seo_metadata or SEOMetadata(page_id=page.id)
        seo.meta_title = seo_data.get('meta_title') or seo_data.get('title') or page.title
        seo.meta_description = seo_data.get('meta_description') or seo_data.get('description') or page.description
        seo.keywords = seo_data.get('keywords') or []
        seo.canonical_url = seo_data.get('canonical_url')
        seo.schema_markup = seo_data.get('schema_markup') or {}
        seo.indexable = seo_data.get('indexable', True)
        db.session.add(seo)
