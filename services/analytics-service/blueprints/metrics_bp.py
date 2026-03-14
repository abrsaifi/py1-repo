"""
Metrics Blueprint
Endpoints for system and service metrics retrieval, aggregation, and analysis
"""

from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, timezone
from functools import wraps
import logging

metrics_bp = Blueprint('metrics', __name__, url_prefix='/metrics')
logger = logging.getLogger(__name__)


def require_tenant():
    """Decorator to ensure tenant context is set"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'tenant_id') or not g.tenant_id:
                return jsonify({'error': 'Unauthorized', 'message': 'Missing tenant context'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# System Metrics Endpoints
# ============================================================================

@metrics_bp.route('/system', methods=['GET'])
@require_tenant()
def list_system_metrics():
    """
    GET /api/metrics/system?service=auth&level=hour&limit=100
    List system metrics with filtering
    """
    try:
        from analytics_models import SystemMetric, AggregationLevel
        
        service = request.args.get('service')
        level = request.args.get('level', 'hour')
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        session = current_app.SessionLocal()
        query = session.query(SystemMetric).filter(
            SystemMetric.tenant_id == g.tenant_id
        )
        
        if service:
            query = query.filter(SystemMetric.service_name == service)
        
        if level:
            query = query.filter(SystemMetric.aggregation_level == level)
        
        metrics = query.order_by(SystemMetric.timestamp.desc()).limit(limit).all()
        
        result = {
            'metrics': [m.to_dict() for m in metrics],
            'count': len(metrics),
            'filters': {
                'service': service,
                'aggregation_level': level,
                'limit': limit,
            }
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing system metrics: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/system/<metric_id>', methods=['GET'])
@require_tenant()
def get_system_metric(metric_id):
    """GET /api/metrics/system/{metric_id} - Get specific system metric"""
    try:
        from analytics_models import SystemMetric
        
        session = current_app.SessionLocal()
        metric = session.query(SystemMetric).filter(
            SystemMetric.id == metric_id,
            SystemMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Metric not found'}), 404
        
        session.close()
        return jsonify(metric.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error getting system metric: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/system/aggregate', methods=['POST'])
@require_tenant()
def aggregate_system_metrics():
    """
    POST /api/metrics/system/aggregate
    Aggregate metrics over time period
    
    Body: {
        "service_name": "auth-service",
        "metric_name": "response_time",
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-31T23:59:59Z",
        "aggregation": "avg"
    }
    """
    try:
        from analytics_models import SystemMetric
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        start_time = datetime.fromisoformat(data.get('start_time', ''))
        end_time = datetime.fromisoformat(data.get('end_time', ''))
        aggregation = data.get('aggregation', 'avg')
        
        query = session.query(SystemMetric).filter(
            SystemMetric.tenant_id == g.tenant_id,
            SystemMetric.service_name == data.get('service_name'),
            SystemMetric.metric_name == data.get('metric_name'),
            SystemMetric.timestamp.between(start_time, end_time)
        )
        
        metrics = query.all()
        
        # Calculate aggregation
        if aggregation == 'avg':
            result = sum(m.value for m in metrics) / len(metrics) if metrics else 0
        elif aggregation == 'sum':
            result = sum(m.value for m in metrics)
        elif aggregation == 'min':
            result = min((m.value for m in metrics), default=0)
        elif aggregation == 'max':
            result = max((m.value for m in metrics), default=0)
        else:
            result = len(metrics)
        
        session.close()
        
        return jsonify({
            'service_name': data.get('service_name'),
            'metric_name': data.get('metric_name'),
            'aggregation': aggregation,
            'result': result,
            'data_points': len(metrics),
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error aggregating metrics: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Service Metrics Endpoints
# ============================================================================

@metrics_bp.route('/service', methods=['GET'])
@require_tenant()
def list_service_metrics():
    """
    GET /api/metrics/service?service_name=auth&period=day&limit=50
    List service-level performance metrics
    """
    try:
        from analytics_models import ServiceMetric
        
        service_name = request.args.get('service_name')
        limit = min(int(request.args.get('limit', 50)), 500)
        
        session = current_app.SessionLocal()
        query = session.query(ServiceMetric).filter(
            ServiceMetric.tenant_id == g.tenant_id
        )
        
        if service_name:
            query = query.filter(ServiceMetric.service_name == service_name)
        
        metrics = query.order_by(ServiceMetric.period_start.desc()).limit(limit).all()
        
        result = {
            'metrics': [m.to_dict() for m in metrics],
            'count': len(metrics),
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing service metrics: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/service/<service_id>', methods=['GET'])
@require_tenant()
def get_service_metric(service_id):
    """GET /api/metrics/service/{service_id} - Get specific service metric"""
    try:
        from analytics_models import ServiceMetric
        
        session = current_app.SessionLocal()
        metric = session.query(ServiceMetric).filter(
            ServiceMetric.id == service_id,
            ServiceMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Service metric not found'}), 404
        
        session.close()
        return jsonify(metric.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error getting service metric: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/service/health/<service_name>', methods=['GET'])
@require_tenant()
def get_service_health(service_name):
    """
    GET /api/metrics/service/health/{service_name}
    Get service health metrics (uptime, error rate, response times)
    """
    try:
        from analytics_models import ServiceMetric
        
        session = current_app.SessionLocal()
        
        # Get latest metric
        metric = session.query(ServiceMetric).filter(
            ServiceMetric.tenant_id == g.tenant_id,
            ServiceMetric.service_name == service_name
        ).order_by(ServiceMetric.period_start.desc()).first()
        
        if not metric:
            session.close()
            return jsonify({
                'service_name': service_name,
                'status': 'unknown',
                'error_rate': 0,
                'uptime_percent': 100,
            }), 200
        
        health = {
            'service_name': service_name,
            'status': 'healthy' if metric.uptime_percent >= 99.9 else 'degraded' if metric.uptime_percent >= 95 else 'unhealthy',
            'uptime_percent': metric.uptime_percent,
            'error_rate': metric.error_rate,
            'response_time_p99': metric.response_time_p99,
            'response_time_p95': metric.response_time_p95,
            'response_time_p50': metric.response_time_p50,
            'timestamp': metric.period_start.isoformat(),
        }
        
        session.close()
        return jsonify(health), 200
    
    except Exception as e:
        logger.error(f"Error getting service health: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# User Activity Metrics Endpoints
# ============================================================================

@metrics_bp.route('/activity', methods=['GET'])
@require_tenant()
def list_activity_metrics():
    """
    GET /api/metrics/activity?limit=30
    List user activity metrics
    """
    try:
        from analytics_models import UserActivityMetric
        
        limit = min(int(request.args.get('limit', 30)), 365)
        
        session = current_app.SessionLocal()
        metrics = session.query(UserActivityMetric).filter(
            UserActivityMetric.tenant_id == g.tenant_id
        ).order_by(UserActivityMetric.period_start.desc()).limit(limit).all()
        
        result = {
            'metrics': [m.to_dict() for m in metrics],
            'count': len(metrics),
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing activity metrics: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/activity/engagement', methods=['GET'])
@require_tenant()
def get_engagement_metrics():
    """
    GET /api/metrics/activity/engagement?days=30
    Get engagement metrics (DAU, WAU, MAU)
    """
    try:
        from analytics_models import UserActivityMetric
        
        days = int(request.args.get('days', 30))
        
        session = current_app.SessionLocal()
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        metrics = session.query(UserActivityMetric).filter(
            UserActivityMetric.tenant_id == g.tenant_id,
            UserActivityMetric.period_start >= start_date
        ).order_by(UserActivityMetric.period_start).all()
        
        result = {
            'engagement_data': [m.to_dict() for m in metrics],
            'summary': {
                'latest_dau': metrics[-1].dau if metrics else 0,
                'latest_wau': metrics[-1].wau if metrics else 0,
                'latest_mau': metrics[-1].mau if metrics else 0,
                'engagement_ratio': metrics[-1].dau_wau_ratio if metrics else 0,
                'stickiness': metrics[-1].dau_mau_ratio if metrics else 0,
            }
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Business Metrics Endpoints
# ============================================================================

@metrics_bp.route('/business', methods=['GET'])
@require_tenant()
def list_business_metrics():
    """
    GET /api/metrics/business?months=12&limit=12
    List business KPI metrics
    """
    try:
        from analytics_models import BusinessMetric
        
        months = int(request.args.get('months', 12))
        
        session = current_app.SessionLocal()
        metrics = session.query(BusinessMetric).filter(
            BusinessMetric.tenant_id == g.tenant_id
        ).order_by(BusinessMetric.period_start.desc()).limit(months).all()
        
        result = {
            'metrics': [m.to_dict() for m in metrics],
            'count': len(metrics),
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing business metrics: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/business/kpis', methods=['GET'])
@require_tenant()
def get_business_kpis():
    """
    GET /api/metrics/business/kpis
    Get key business KPIs (MRR, LTV, CAC, Growth, etc.)
    """
    try:
        from analytics_models import BusinessMetric
        
        session = current_app.SessionLocal()
        
        latest = session.query(BusinessMetric).filter(
            BusinessMetric.tenant_id == g.tenant_id
        ).order_by(BusinessMetric.period_start.desc()).first()
        
        if not latest:
            session.close()
            return jsonify({
                'mrr': 0,
                'arr': 0,
                'ltv': 0,
                'cac': 0,
                'growth_rate': 0,
                'churn_rate': 0,
            }), 200
        
        kpis = {
            'mrr': latest.mrr,
            'arr': latest.arr,
            'ltv': latest.customer_lifetime_value,
            'cac': latest.customer_acquisition_cost,
            'ltv_cac_ratio': latest.customer_lifetime_value / latest.customer_acquisition_cost if latest.customer_acquisition_cost > 0 else 0,
            'growth_rate': latest.growth_rate,
            'churn_rate': latest.churn_rate,
            'nrr': latest.net_revenue_retention,
            'expansion_revenue': latest.expansion_revenue,
            'period': latest.period_start.isoformat(),
        }
        
        session.close()
        return jsonify(kpis), 200
    
    except Exception as e:
        logger.error(f"Error getting business KPIs: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/business/revenue', methods=['GET'])
@require_tenant()
def get_revenue_metrics():
    """
    GET /api/metrics/business/revenue?months=12
    Get revenue metrics and trends
    """
    try:
        from analytics_models import BusinessMetric
        
        months = int(request.args.get('months', 12))
        
        session = current_app.SessionLocal()
        metrics = session.query(BusinessMetric).filter(
            BusinessMetric.tenant_id == g.tenant_id
        ).order_by(BusinessMetric.period_start.desc()).limit(months).all()
        
        revenue_data = [{
            'period': m.period_start.isoformat(),
            'total_revenue': m.total_revenue,
            'mrr': m.mrr,
            'arr': m.arr,
            'recurring_revenue': m.recurring_revenue,
        } for m in reversed(metrics)]
        
        session.close()
        return jsonify({
            'revenue_data': revenue_data,
            'total_revenue': sum(m['total_revenue'] for m in revenue_data),
            'avg_mrr': sum(m['mrr'] for m in revenue_data) / len(revenue_data) if revenue_data else 0,
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting revenue metrics: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Metrics Export
# ============================================================================

@metrics_bp.route('/export', methods=['GET'])
@require_tenant()
def export_metrics():
    """
    GET /api/metrics/export?format=csv&type=all
    Export metrics in various formats
    """
    try:
        format_type = request.args.get('format', 'json')
        metric_type = request.args.get('type', 'all')
        
        if format_type not in ['json', 'csv', 'xlsx']:
            return jsonify({'error': 'Invalid format'}), 400
        
        # In real implementation would generate file and return download
        return jsonify({
            'message': 'Export started',
            'format': format_type,
            'type': metric_type,
            'download_url': f'/api/metrics/export/download?task_id=task-123',
        }), 202
    
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/time-series', methods=['POST'])
@require_tenant()
def get_time_series():
    """
    POST /api/metrics/time-series
    Get time-series data for charting
    
    Body: {
        "metric_name": "response_time",
        "service_name": "auth",
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-31T23:59:59Z",
        "granularity": "hour"
    }
    """
    try:
        from analytics_models import SystemMetric
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        start_time = datetime.fromisoformat(data.get('start_time', ''))
        end_time = datetime.fromisoformat(data.get('end_time', ''))
        
        metrics = session.query(SystemMetric).filter(
            SystemMetric.tenant_id == g.tenant_id,
            SystemMetric.metric_name == data.get('metric_name'),
            SystemMetric.service_name == data.get('service_name'),
            SystemMetric.timestamp.between(start_time, end_time)
        ).order_by(SystemMetric.timestamp).all()
        
        time_series = [{
            'timestamp': m.timestamp.isoformat(),
            'value': m.value,
            'average': m.avg_value,
            'min': m.min_value,
            'max': m.max_value,
        } for m in metrics]
        
        session.close()
        return jsonify({
            'metric_name': data.get('metric_name'),
            'service': data.get('service_name'),
            'data': time_series,
            'data_points': len(time_series),
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting time series: {e}")
        return jsonify({'error': str(e)}), 500
