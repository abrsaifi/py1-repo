from flask import Blueprint, current_app, jsonify

from app.middleware.auth import admin_required
from app.services.action_artifact_service import ActionArtifactService
from app.services.aeo_service import AEOService

bp = Blueprint('aeo', __name__, url_prefix='/api/aeo')


@bp.route('/summary', methods=['GET'])
@admin_required
def aeo_summary():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify({'summary': AEOService.get_dashboard_summary(site_url)}), 200


@bp.route('/pages', methods=['GET'])
@admin_required
def aeo_pages():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify({'pages': AEOService.get_dashboard_pages(site_url)}), 200


@bp.route('/questions', methods=['GET'])
@admin_required
def aeo_questions():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify({'questions': AEOService.get_question_opportunities(site_url)}), 200


@bp.route('/actions/generate', methods=['POST'])
@admin_required
def generate_aeo_action():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify(ActionArtifactService.refresh_aeo(site_url)), 200


@bp.route('/actions/expand-faqs', methods=['POST'])
@admin_required
def expand_faqs_action():
    site_url = current_app.config.get('SITE_URL', 'http://localhost:3000')
    return jsonify(ActionArtifactService.expand_faqs(site_url)), 200