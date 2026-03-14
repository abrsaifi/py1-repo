"""Persisted Phase 15 analytics and reports endpoints."""
from flask import Blueprint, jsonify, request

from app.middleware.auth import auth_required
from app.services.phase15_service import Phase15Service
from app.models import db

bp = Blueprint('phase15_analytics', __name__, url_prefix='/api')


def api_response(success=True, data=None, error=None, message=None, status_code=200):
    payload = {'success': success}
    if data is not None:
        payload['data'] = data
    if error is not None:
        payload['error'] = error
    if message is not None:
        payload['message'] = message
    return jsonify(payload), status_code


@bp.route('/analytics/dashboard', methods=['GET'])
@auth_required
def get_analytics_dashboard():
    return api_response(data=Phase15Service.get_dashboard(request.user_id))


@bp.route('/analytics/statistics', methods=['POST'])
@auth_required
def get_statistics():
    payload = request.get_json(silent=True) or {}
    return api_response(data=Phase15Service.get_statistics(payload.get('dataset', 'sales')))


@bp.route('/analytics/forecast', methods=['POST'])
@auth_required
def get_forecast():
    payload = request.get_json(silent=True) or {}
    return api_response(data=Phase15Service.get_forecast(payload.get('metric', 'revenue'), payload.get('days_ahead', 14)))


@bp.route('/analytics/heatmap', methods=['GET'])
@auth_required
def get_heatmap_data():
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = list(range(24))
    values = [[((day_index + 1) * (hour + 3)) % 100 for hour in hours] for day_index, _ in enumerate(days)]
    return api_response(data={'days': days, 'hours': hours, 'data': values, 'scale': {'min': 0, 'max': 99, 'unit': 'activity_count'}})


@bp.route('/analytics/scatter', methods=['GET'])
@auth_required
def get_scatter_data():
    points = [{'x': x * 2.5, 'y': round((x * 2.5) * 1.18 + 12, 2)} for x in range(5, 55)]
    return api_response(data={'x_label': 'Marketing Spend ($1000s)', 'y_label': 'Revenue ($1000s)', 'correlation': 0.78, 'r_squared': 0.61, 'points': points, 'trend_line': {'slope': 1.18, 'intercept': 12.0, 'equation': 'y = 1.18x + 12.0'}})


@bp.route('/analytics/treemap', methods=['GET'])
@auth_required
def get_treemap_data():
    data = {
        'name': 'Product Revenue',
        'children': [
            {'name': 'Documents', 'value': 62000, 'children': [{'name': 'PDF', 'value': 28000}, {'name': 'Office', 'value': 22000}, {'name': 'Images', 'value': 12000}]},
            {'name': 'Collaboration', 'value': 41000, 'children': [{'name': 'Shares', 'value': 16000}, {'name': 'Comments', 'value': 9000}, {'name': 'Teams', 'value': 16000}]},
        ],
    }
    return api_response(data=data)


@bp.route('/analytics/sankey', methods=['GET'])
@auth_required
def get_sankey_data():
    return api_response(data={'nodes': [{'name': 'Upload'}, {'name': 'Convert'}, {'name': 'Share'}, {'name': 'Download'}], 'links': [{'source': 0, 'target': 1, 'value': 1000}, {'source': 1, 'target': 2, 'value': 640}, {'source': 2, 'target': 3, 'value': 525}]})


@bp.route('/analytics/funnel', methods=['GET'])
@auth_required
def get_funnel_data():
    stages = [{'name': 'Visits', 'value': 10000}, {'name': 'Uploads', 'value': 4200}, {'name': 'Conversions', 'value': 3100}, {'name': 'Shares', 'value': 1450}, {'name': 'Exports', 'value': 1025}]
    return api_response(data={'stages': stages, 'conversion_rates': [0.42, 0.74, 0.47, 0.71], 'dropoff_analysis': {'biggest_drop': 'Visits -> Uploads', 'optimization_focus': 'Improve onboarding and upload CTA'}})


@bp.route('/analytics/radar', methods=['GET'])
@auth_required
def get_radar_data():
    return api_response(data={'categories': ['Adoption', 'Retention', 'Throughput', 'Reliability', 'Collaboration'], 'series': [{'name': 'Current', 'values': [82, 76, 88, 91, 73]}, {'name': 'Target', 'values': [90, 85, 92, 95, 84]}]})


@bp.route('/reports', methods=['GET'])
@auth_required
def list_reports():
    return api_response(data=Phase15Service.list_reports(request.user_id))


@bp.route('/reports', methods=['POST'])
@auth_required
def create_report():
    report = Phase15Service.create_report(request.user_id, request.get_json(silent=True) or {})
    return api_response(data=report.to_dict(), status_code=201)


@bp.route('/reports/<report_id>', methods=['GET'])
@auth_required
def get_report(report_id):
    report = Phase15Service.get_report_for_user(request.user_id, report_id)
    if not report:
        return api_response(success=False, error='Forbidden', status_code=403)
    return api_response(data=report.to_dict())


@bp.route('/reports/<report_id>', methods=['PUT'])
@auth_required
def update_report(report_id):
    report = Phase15Service.get_report_for_user(request.user_id, report_id)
    if not report:
        return api_response(success=False, error='Forbidden', status_code=403)

    payload = request.get_json(silent=True) or {}
    for field in ('name', 'description', 'report_type', 'export_format'):
        if field in payload:
            setattr(report, field, payload[field])
    if 'config' in payload:
        report.config = payload['config'] or {}
    db.session.commit()
    return api_response(data=report.to_dict())


@bp.route('/reports/<report_id>', methods=['DELETE'])
@auth_required
def delete_report(report_id):
    report = Phase15Service.get_report_for_user(request.user_id, report_id)
    if not report:
        return api_response(success=False, error='Forbidden', status_code=403)
    db.session.delete(report)
    db.session.commit()
    return api_response(data={'id': report_id, 'deleted': True})


@bp.route('/reports/<report_id>/export', methods=['POST'])
@auth_required
def export_report(report_id):
    report = Phase15Service.get_report_for_user(request.user_id, report_id)
    if not report:
        return api_response(success=False, error='Forbidden', status_code=403)

    payload = request.get_json(silent=True) or {}
    export_format = payload.get('format', report.export_format)
    export_data = Phase15Service.export_report(report, export_format)
    return api_response(data=export_data)