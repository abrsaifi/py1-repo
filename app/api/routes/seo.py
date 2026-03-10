from flask import Blueprint, Response, current_app
import datetime

bp = Blueprint('seo', __name__)


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate a simple XML sitemap for the site and tool pages."""
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    lastmod = datetime.datetime.utcnow().isoformat() + 'Z'

    # Mirror the tool slugs from tools list — keep in sync with tools.py
    slugs = [
        'jpg-to-png','png-to-jpg','webp-to-png','image-to-pdf',
        'pdf-to-docx','docx-to-pdf','pdf-to-excel','excel-to-pdf',
        'pdf-to-pptx','pptx-to-pdf','csv-to-excel','pdf-to-image',
        'compress-pdf','merge-pdf','split-pdf','mp3-to-wav','mp4-to-webm'
    ]

    urlset = [
        f"  <url>\n    <loc>{site_url}/</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>"
    ]

    for s in slugs:
        urlset.append(
            f"  <url>\n    <loc>{site_url}/{s}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>"
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(urlset)
    xml += '\n</urlset>'

    return Response(xml, mimetype='application/xml')


@bp.route('/robots.txt', methods=['GET'])
def robots():
    """Return robots.txt content. Sitemap location uses SITE_URL config."""
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /api/',
        '',
        f'Sitemap: {site_url}/sitemap.xml'
    ]
    return Response('\n'.join(lines) + '\n', mimetype='text/plain')
