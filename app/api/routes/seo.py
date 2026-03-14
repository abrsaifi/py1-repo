from flask import Blueprint, Response, current_app, jsonify

from app.middleware.auth import admin_required
from app.services.action_artifact_service import ActionArtifactService
from app.services.seo_service import SEOService

bp = Blueprint('seo', __name__)


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate a sitemap for public CMS and tool pages."""
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    xml = SEOService.build_sitemap_xml(site_url)
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


@bp.route('/api/seo/summary', methods=['GET'])
@admin_required
def seo_summary():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify({'summary': SEOService.get_dashboard_summary(site_url)}), 200


@bp.route('/api/seo/pages', methods=['GET'])
@admin_required
def seo_pages():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify({'pages': SEOService.get_dashboard_pages(site_url)}), 200


@bp.route('/api/seo/actions/generate', methods=['POST'])
@admin_required
def generate_pages_action():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify(ActionArtifactService.refresh_seo(site_url)), 200


@bp.route('/api/seo/actions/submit-sitemap', methods=['POST'])
@admin_required
def submit_sitemap_action():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify(ActionArtifactService.submit_sitemap(site_url)), 200


@bp.route('/api/seo/actions/reindex', methods=['POST'])
@admin_required
def reindex_action():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify(ActionArtifactService.queue_reindex(site_url)), 200
