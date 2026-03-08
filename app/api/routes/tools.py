import os
from flask import Blueprint, jsonify, current_app

bp = Blueprint('tools', __name__)


@bp.route('/tools/<slug>', methods=['GET'])
def get_tool(slug):
    # Minimal test metadata for frontend SEO verification
    public_base = os.environ.get('PUBLIC_BASE_URL') or 'http://localhost:3000'

    tool = {
        'slug': slug,
        'title': f"{slug.replace('-', ' ').title()} Converter",
        'name': f"{slug.replace('-', ' ').title()} Converter",
        'from_format': 'Source Format',
        'to_format': 'Target Format',
        'description': 'Convert Source Format to Target Format files online for free. Convert your files with ease. No registration required.',
        'icon': f'{public_base}/tool-icons/{slug}.png',
        'url': f'{public_base}/{slug}',
        'key_features': ['Fast conversion', 'High quality', 'Secure', 'No registration'],
        'rating': {'value': '4.8', 'count': '2500'},
        'offers': {'price': '0', 'currency': 'USD'}
    }
    resp = jsonify({'success': True, 'tool': tool})
    resp.headers['Access-Control-Allow-Origin'] = '*'  # ensure dev access
    return resp


@bp.route('/tools/<slug>/related', methods=['GET'])
def related_tools(slug):
    related = [
        {'slug': 'png-to-jpg', 'title': 'png-to-jpg Converter'},
        {'slug': 'webp-to-png', 'title': 'webp-to-png Converter'},
        {'slug': 'bmp-to-png', 'title': 'bmp-to-png Converter'},
    ]
    resp = jsonify({'success': True, 'related_tools': related})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/tools', methods=['GET'])
def list_tools():
    """Return a minimal list of available tools for frontend listing."""
    # Basic tool list used by the frontend CMS and tool index
    slugs = [
        'jpg-to-png','png-to-jpg','webp-to-png','image-to-pdf',
        'pdf-to-docx','docx-to-pdf','pdf-to-excel','excel-to-pdf',
        'pdf-to-pptx','pptx-to-pdf','csv-to-excel','pdf-to-image',
        'compress-pdf','merge-pdf','split-pdf','mp3-to-wav','mp4-to-webm'
    ]
    tools = []
    public_base = os.environ.get('PUBLIC_BASE_URL') or 'http://localhost:3000'
    for s in slugs:
        tools.append({
            'slug': s,
            'title': f"{s.replace('-', ' ').title()} Converter",
            'category': 'utility',
            'icon': f'{public_base}/tool-icons/{s}.png'
        })

    resp = jsonify({'success': True, 'tools': tools})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
