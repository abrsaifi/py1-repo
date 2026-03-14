"""CMS API routes."""
from flask import Blueprint, jsonify, request

from app.middleware.auth import admin_required
from app.services.cms_service import CMSService

bp = Blueprint('cms', __name__, url_prefix='/api/cms')


@bp.route('/pages', methods=['GET'])
@admin_required
def list_pages():
    pages = CMSService.list_pages(include_drafts=True)
    return jsonify({'pages': [page.to_dict() for page in pages]}), 200


@bp.route('/pages', methods=['POST'])
@admin_required
def create_page():
    data = request.get_json() or {}
    try:
        page = CMSService.create_page(data)
        return jsonify({'message': 'Page created successfully', 'page': page.to_dict()}), 201
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@bp.route('/pages/<int:page_id>', methods=['GET'])
@admin_required
def get_page(page_id):
    page = CMSService.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    return jsonify({'page': page.to_dict()}), 200


@bp.route('/pages/<int:page_id>', methods=['PUT'])
@admin_required
def update_page(page_id):
    page = CMSService.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404

    data = request.get_json() or {}
    try:
        page = CMSService.update_page(page, data)
        return jsonify({'message': 'Page updated successfully', 'page': page.to_dict()}), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@bp.route('/pages/<int:page_id>', methods=['DELETE'])
@admin_required
def delete_page(page_id):
    page = CMSService.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404

    CMSService.delete_page(page)
    return jsonify({'message': 'Page deleted successfully'}), 200


@bp.route('/pages/slug/<slug>', methods=['GET'])
def get_public_page(slug):
    page = CMSService.get_page_by_slug(slug, include_drafts=False)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    return jsonify({'page': page.to_dict()}), 200


@bp.route('/widgets/types', methods=['GET'])
def list_widget_types():
    return jsonify({
        'widget_types': [
            {'type': 'hero', 'label': 'Hero'},
            {'type': 'text', 'label': 'Text'},
            {'type': 'features', 'label': 'Features'},
            {'type': 'faq', 'label': 'FAQ'},
            {'type': 'pricing', 'label': 'Pricing'},
            {'type': 'cta', 'label': 'Call To Action'},
            {'type': 'converter', 'label': 'Converter'},
        ]
    }), 200
