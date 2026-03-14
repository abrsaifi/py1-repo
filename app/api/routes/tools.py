from flask import Blueprint, jsonify, request

from app.services.tool_catalog import get_related_tools, get_tool_by_slug, load_tool_catalog

bp = Blueprint('tools', __name__)


@bp.route('/tools/<slug>', methods=['GET'])
def get_tool(slug):
    tool = get_tool_by_slug(slug)
    if not tool:
        return jsonify({'success': False, 'error': f'Tool not found: {slug}'}), 404

    resp = jsonify({'success': True, 'tool': tool})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/tools/<slug>/related', methods=['GET'])
def related_tools(slug):
    limit = request.args.get('limit', type=int)
    related = get_related_tools(slug, limit=limit)
    resp = jsonify({'success': True, 'related_tools': related})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@bp.route('/tools', methods=['GET'])
def list_tools():
    tools = load_tool_catalog()
    resp = jsonify({'success': True, 'tools': tools})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
