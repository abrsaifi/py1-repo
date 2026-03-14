"""
Custom Metrics Blueprint
Endpoints for user-defined metrics with formula support
"""

from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime, timezone
from functools import wraps
import uuid
import logging



custom_metrics_bp = Blueprint('custom_metrics', __name__, url_prefix='/custom-metrics')
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
# Custom Metric CRUD
# ============================================================================

@custom_metrics_bp.route('', methods=['GET'])
@require_tenant()
def list_custom_metrics():
    """
    GET /api/custom-metrics?limit=50
    List custom metrics for tenant
    """
    try:
        from analytics_models import CustomMetric
        
        limit = min(int(request.args.get('limit', 50)), 500)
        
        session = current_app.SessionLocal()
        metrics = session.query(CustomMetric).filter(
            CustomMetric.tenant_id == g.tenant_id
        ).order_by(CustomMetric.created_at.desc()).limit(limit).all()
        
        result = {
            'metrics': [m.to_dict() for m in metrics],
            'count': len(metrics),
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing custom metrics: {e}")
        return jsonify({'error': str(e)}), 500


@custom_metrics_bp.route('', methods=['POST'])
@require_tenant()
def create_custom_metric():
    """
    POST /api/custom-metrics
    Create custom metric with formula
    
    Body: {
        "name": "Success Rate",
        "description": "Percentage of successful requests",
        "metric_formula": "successful_requests / total_requests * 100",
        "component_metrics": ["successful_requests", "total_requests"],
        "metric_unit": "%",
        "calculation_method": "simple"
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({'error': 'Bad Request', 'message': 'name is required'}), 400
        if not data.get('metric_formula'):
            return jsonify({'error': 'Bad Request', 'message': 'metric_formula is required'}), 400
        
        session = current_app.SessionLocal()
        
        metric = CustomMetric(
            id=str(uuid.uuid4()),
            tenant_id=g.tenant_id,
            name=data.get('name'),
            description=data.get('description', ''),
            metric_formula=data.get('metric_formula'),
            component_metrics=data.get('component_metrics', []),
            metric_unit=data.get('metric_unit'),
            calculation_method=data.get('calculation_method', 'simple'),
            is_active=True,
            created_by_user_id=g.user_id,
        )
        
        session.add(metric)
        session.commit()
        
        result = metric.to_dict()
        session.close()
        
        return jsonify({'success': True, 'metric': result}), 201
    
    except Exception as e:
        logger.error(f"Error creating custom metric: {e}")
        return jsonify({'error': str(e)}), 500


@custom_metrics_bp.route('/<metric_id>', methods=['GET'])
@require_tenant()
def get_custom_metric(metric_id):
    """GET /api/custom-metrics/{metric_id}"""
    try:
        from analytics_models import CustomMetric
        
        session = current_app.SessionLocal()
        metric = session.query(CustomMetric).filter(
            CustomMetric.id == metric_id,
            CustomMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Metric not found'}), 404
        
        result = metric.to_dict()
        session.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting custom metric: {e}")
        return jsonify({'error': str(e)}), 500


@custom_metrics_bp.route('/<metric_id>', methods=['PUT'])
@require_tenant()
def update_custom_metric(metric_id):
    """PUT /api/custom-metrics/{metric_id}"""
    try:
        from analytics_models import CustomMetric
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        metric = session.query(CustomMetric).filter(
            CustomMetric.id == metric_id,
            CustomMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Metric not found'}), 404
        
        if 'name' in data:
            metric.name = data['name']
        if 'metric_formula' in data:
            metric.metric_formula = data['metric_formula']
        if 'component_metrics' in data:
            metric.component_metrics = data['component_metrics']
        if 'is_active' in data:
            metric.is_active = data['is_active']
        
        session.commit()
        
        result = metric.to_dict()
        session.close()
        
        return jsonify({'success': True, 'metric': result}), 200
    
    except Exception as e:
        logger.error(f"Error updating custom metric: {e}")
        return jsonify({'error': str(e)}), 500


@custom_metrics_bp.route('/<metric_id>', methods=['DELETE'])
@require_tenant()
def delete_custom_metric(metric_id):
    """DELETE /api/custom-metrics/{metric_id}"""
    try:
        from analytics_models import CustomMetric
        
        session = current_app.SessionLocal()
        metric = session.query(CustomMetric).filter(
            CustomMetric.id == metric_id,
            CustomMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Metric not found'}), 404
        
        session.delete(metric)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Metric deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting custom metric: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Custom Metric Calculation
# ============================================================================

@custom_metrics_bp.route('/<metric_id>/calculate', methods=['POST'])
@require_tenant()
def calculate_custom_metric(metric_id):
    """
    POST /api/custom-metrics/{metric_id}/calculate
    Calculate custom metric value based on formula
    
    Body: {
        "values": {
            "successful_requests": 950,
            "total_requests": 1000
        }
    }
    """
    try:
        from analytics_models import CustomMetric
        
        data = request.get_json() or {}
        values = data.get('values', {})
        
        session = current_app.SessionLocal()
        metric = session.query(CustomMetric).filter(
            CustomMetric.id == metric_id,
            CustomMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Metric not found'}), 404
        
        try:
            # Safely evaluate formula with provided values
            result = eval(metric.metric_formula.replace(' ', ''), {"__builtins__": {}}, values)
            
            # Update calculation count
            metric.calculation_count = (metric.calculation_count or 0) + 1
            metric.last_calculated_at = datetime.now(timezone.utc)
            session.commit()
            
            session.close()
            
            return jsonify({
                'metric_id': metric_id,
                'metric_name': metric.name,
                'result': result,
                'unit': metric.metric_unit,
                'formula': metric.metric_formula,
            }), 200
        
        except Exception as calc_error:
            session.close()
            return jsonify({
                'error': 'Bad Request',
                'message': f'Formula evaluation failed: {str(calc_error)}'
            }), 400
    
    except Exception as e:
        logger.error(f"Error calculating metric: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Metric Sharing
# ============================================================================

@custom_metrics_bp.route('/<metric_id>/share', methods=['POST'])
@require_tenant()
def share_custom_metric(metric_id):
    """
    POST /api/custom-metrics/{metric_id}/share
    Share custom metric with other users/groups
    """
    try:
        from analytics_models import CustomMetric
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        metric = session.query(CustomMetric).filter(
            CustomMetric.id == metric_id,
            CustomMetric.tenant_id == g.tenant_id
        ).first()
        
        if not metric:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Metric not found'}), 404
        
        metric.is_public = data.get('is_public', False)
        session.commit()
        
        result = metric.to_dict()
        session.close()
        
        return jsonify({'success': True, 'metric': result}), 200
    
    except Exception as e:
        logger.error(f"Error sharing metric: {e}")
        return jsonify({'error': str(e)}), 500
