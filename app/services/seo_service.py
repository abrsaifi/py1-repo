"""SEO service helpers for sitemap generation and admin reporting."""
from datetime import datetime, timedelta, timezone

from app.models import Page

TOOL_SLUGS = [
    'jpg-to-png', 'png-to-jpg', 'webp-to-png', 'image-to-pdf',
    'pdf-to-docx', 'docx-to-pdf', 'pdf-to-excel', 'excel-to-pdf',
    'pdf-to-pptx', 'pptx-to-pdf', 'csv-to-excel', 'pdf-to-image',
    'compress-pdf', 'merge-pdf', 'split-pdf', 'mp3-to-wav', 'mp4-to-webm',
]


class SEOService:
    """Provides SEO-oriented reporting and sitemap data."""

    @staticmethod
    def get_tool_pages(site_url):
        pages = []
        next_update = (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat()
        for slug in TOOL_SLUGS:
            pages.append({
                'id': f'TOOL-{slug.upper()}',
                'title': f"{slug.replace('-', ' ').title()} Converter",
                'slug': slug,
                'url': f'{site_url}/{slug}',
                'status': 'indexed',
                'indexed': datetime.now(timezone.utc).date().isoformat(),
                'keywords': 12,
                'traffic': 0,
                'nextUpdate': next_update,
                'source': 'tool',
            })
        return pages

    @staticmethod
    def get_cms_pages(site_url):
        pages = []
        records = Page.query.order_by(Page.updated_at.desc()).all()
        for page in records:
            keywords = []
            if page.seo_metadata and page.seo_metadata.keywords:
                keywords = page.seo_metadata.keywords
            status = 'indexed' if page.status == 'published' else 'pending'
            pages.append({
                'id': f'PAGE-{page.id:03d}',
                'title': page.title,
                'slug': page.slug,
                'url': f'{site_url}/{page.slug}',
                'status': status,
                'indexed': page.published_at.date().isoformat() if page.published_at else None,
                'keywords': len(keywords),
                'traffic': 0,
                'nextUpdate': (page.updated_at.date() + timedelta(days=7)).isoformat() if page.updated_at else datetime.now(timezone.utc).date().isoformat(),
                'source': 'cms',
            })
        return pages

    @staticmethod
    def get_dashboard_summary(site_url):
        cms_pages = SEOService.get_cms_pages(site_url)
        tool_pages = SEOService.get_tool_pages(site_url)
        all_pages = cms_pages + tool_pages
        indexed_pages = [page for page in all_pages if page['status'] == 'indexed']
        pending_pages = [page for page in all_pages if page['status'] != 'indexed']

        return {
            'totalPages': len(all_pages),
            'indexedPages': len(indexed_pages),
            'pendingPages': len(pending_pages),
            'publishingSchedule': 'Scheduled Daily',
            'keywordExpansion': f"{round((len(indexed_pages) / len(all_pages) * 100), 1) if all_pages else 0}%",
        }

    @staticmethod
    def get_dashboard_pages(site_url):
        cms_pages = SEOService.get_cms_pages(site_url)
        tool_pages = SEOService.get_tool_pages(site_url)
        return cms_pages + tool_pages

    @staticmethod
    def build_sitemap_xml(site_url):
        lastmod = datetime.now(timezone.utc).isoformat() + 'Z'
        urlset = [
            f"  <url>\n    <loc>{site_url}/</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>"
        ]

        for page in SEOService.get_dashboard_pages(site_url):
            priority = '0.8' if page['source'] == 'tool' else '0.7'
            urlset.append(
                f"  <url>\n    <loc>{page['url']}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>{priority}</priority>\n  </url>"
            )

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += '\n'.join(urlset)
        xml += '\n</urlset>'
        return xml
