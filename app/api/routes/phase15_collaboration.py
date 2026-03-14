"""Persisted Phase 15 collaboration endpoints."""
from flask import Blueprint, jsonify, request

from app.middleware.auth import admin_required, auth_required
from app.services.phase15_service import Phase15Service

bp = Blueprint('phase15_collaboration', __name__, url_prefix='/api')


def api_response(success=True, data=None, error=None, message=None, status_code=200):
    payload = {'success': success}
    if data is not None:
        payload['data'] = data
    if error is not None:
        payload['error'] = error
    if message is not None:
        payload['message'] = message
    return jsonify(payload), status_code


@bp.route('/collaboration/dashboard', methods=['GET'])
@auth_required
def collaboration_dashboard():
    return api_response(data=Phase15Service.collaboration_dashboard(request.user_id))


@bp.route('/documents', methods=['GET'])
@auth_required
def list_documents():
    return api_response(data=Phase15Service.list_documents(request.user_id))


@bp.route('/documents', methods=['POST'])
@auth_required
def create_document():
    document = Phase15Service.create_document(request.user_id, request.get_json(silent=True) or {})
    return api_response(data=document.to_dict(shared_with=0), status_code=201)


@bp.route('/documents/<document_id>', methods=['GET'])
@auth_required
def get_document(document_id):
    document = Phase15Service.get_document_for_user(request.user_id, document_id)
    if not document:
        return api_response(success=False, error='Forbidden', status_code=403)
    return api_response(data=document.to_dict(shared_with=document.shares.count()))


@bp.route('/documents/<document_id>/share', methods=['POST'])
@auth_required
def share_document(document_id):
    document = Phase15Service.get_document_for_user(request.user_id, document_id, require_manage=True)
    if not document:
        return api_response(success=False, error='Forbidden', status_code=403)
    shares = Phase15Service.share_document(request.user_id, document, request.get_json(silent=True) or {})
    return api_response(data={'document_id': document.id, 'shares': [share.to_dict() for share in shares], 'total_shared_with': len(shares)}, status_code=201)


@bp.route('/documents/<document_id>/shares', methods=['GET'])
@auth_required
def document_shares(document_id):
    document = Phase15Service.get_document_for_user(request.user_id, document_id)
    if not document:
        return api_response(success=False, error='Forbidden', status_code=403)
    shares = [share.to_dict() for share in document.shares.order_by('created_at desc').all()]
    return api_response(data={'document_id': document_id, 'shares': shares, 'total_shared_with': len(shares)})


@bp.route('/documents/<document_id>/comments', methods=['GET'])
@auth_required
def list_comments(document_id):
    document = Phase15Service.get_document_for_user(request.user_id, document_id)
    if not document:
        return api_response(success=False, error='Forbidden', status_code=403)
    return api_response(data=Phase15Service.list_comments(document_id))


@bp.route('/documents/<document_id>/comments', methods=['POST'])
@auth_required
def add_comment(document_id):
    document = Phase15Service.get_document_for_user(request.user_id, document_id)
    if not document:
        return api_response(success=False, error='Forbidden', status_code=403)
    payload = request.get_json(silent=True) or {}
    if not (payload.get('content') or '').strip():
        return api_response(success=False, error='Comment content is required', status_code=400)
    comment = Phase15Service.add_comment(request.user_id, document, payload)
    return api_response(data=comment.to_dict(), status_code=201)


@bp.route('/teams', methods=['GET'])
@auth_required
def list_teams():
    return api_response(data=Phase15Service.list_teams(request.user_id))


@bp.route('/teams', methods=['POST'])
@auth_required
def create_team():
    payload = request.get_json(silent=True) or {}
    if not (payload.get('name') or '').strip():
        return api_response(success=False, error='Team name is required', status_code=400)
    team = Phase15Service.create_team(request.user_id, payload)
    return api_response(data=team.to_dict(members=1, role='admin'), status_code=201)


@bp.route('/teams/<team_id>/members', methods=['GET'])
@auth_required
def get_team_members(team_id):
    team = Phase15Service.get_team_for_user(request.user_id, team_id)
    if not team:
        return api_response(success=False, error='Forbidden', status_code=403)
    return api_response(data=Phase15Service.get_team_members(team_id))


@bp.route('/teams/<team_id>/projects', methods=['GET'])
@auth_required
def get_team_projects(team_id):
    team = Phase15Service.get_team_for_user(request.user_id, team_id)
    if not team:
        return api_response(success=False, error='Forbidden', status_code=403)
    return api_response(data=[{'id': f'{team_id}-roadmap', 'name': f'{team.name} roadmap', 'status': 'active', 'progress': 70, 'members': team.members.count(), 'due_date': None}])


@bp.route('/audit/logs', methods=['GET'])
@admin_required
def get_audit_logs():
    action = request.args.get('action')
    user_id = request.args.get('user_id', type=int)
    return api_response(data=Phase15Service.list_activity_logs(action=action, user_id=user_id))


@bp.route('/notifications', methods=['GET'])
@auth_required
def get_notifications():
    return api_response(data=Phase15Service.list_notifications(request.user_id, request.args.get('filter')))


@bp.route('/notifications/<notification_id>', methods=['PUT'])
@auth_required
def mark_notification_read(notification_id):
    notification = Phase15Service.mark_notification_read(request.user_id, notification_id)
    return api_response(data=notification.to_dict())


@bp.route('/notifications/preferences', methods=['GET'])
@auth_required
def get_notification_preferences():
    preferences = Phase15Service.get_notification_preferences(request.user_id)
    return api_response(data=preferences.to_dict())


@bp.route('/notifications/preferences', methods=['POST'])
@auth_required
def update_notification_preferences():
    preferences = Phase15Service.update_notification_preferences(request.user_id, request.get_json(silent=True) or {})
    return api_response(data=preferences.to_dict())


@bp.route('/permissions/matrix', methods=['GET'])
@auth_required
def get_permissions_matrix():
    return api_response(data=Phase15Service.permissions_matrix())


@bp.route('/permissions/roles', methods=['GET'])
@auth_required
def get_roles():
    return api_response(data=Phase15Service.permission_roles())