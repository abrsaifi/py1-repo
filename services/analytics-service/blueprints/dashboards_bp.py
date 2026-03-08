"""
Dashboards Blueprint
Endpoints for dashboard CRUD operations, widget management, and configuration
"""

from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy.orm import Session
from datetime import datetime
from functools import wraps
import uuid
import logging

dashboards_bp = Blueprint('dashboards', __name__, url_prefix='/dashboards')
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


def get_dashboard_or_404(session, dashboard_id, tenant_id):
    """Helper to fetch dashboard by ID with tenant check"""
    from analytics_models import Dashboard
    
    dashboard = session.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.tenant_id == tenant_id
    ).first()
    
    return dashboard


# ============================================================================
# Dashboard CRUD Endpoints
# ============================================================================

@dashboards_bp.route('', methods=['GET'])
@require_tenant()
def list_dashboards():
    """
    GET /api/dashboards?type=executive&limit=50
    List dashboards with filtering
    """
    try:
        from analytics_models import Dashboard, DashboardType
        
        dashboard_type = request.args.get('type')
        limit = min(int(request.args.get('limit', 50)), 500)
        
        session = current_app.SessionLocal()
        query = session.query(Dashboard).filter(
            Dashboard.tenant_id == g.tenant_id
        )
        
        if dashboard_type:
            query = query.filter(Dashboard.dashboard_type == dashboard_type)
        
        dashboards = query.order_by(Dashboard.created_at.desc()).limit(limit).all()
        
        result = {
            'dashboards': [d.to_dict() for d in dashboards],
            'count': len(dashboards),
            'filters': {'type': dashboard_type},
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing dashboards: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('', methods=['POST'])
@require_tenant()
def create_dashboard():
    """
    POST /api/dashboards
    Create new dashboard
    
    Body: {
        "name": "Q1 Executive Dashboard",
        "description": "Key metrics for executives",
        "dashboard_type": "executive",
        "widgets": [...],
        "layout": {...}
    }
    """
    try:
        from analytics_models import Dashboard, DashboardType
        
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({'error': 'Bad Request', 'message': 'name is required'}), 400
        
        session = current_app.SessionLocal()
        
        dashboard = Dashboard(
            id=str(uuid.uuid4()),
            tenant_id=g.tenant_id,
            name=data.get('name'),
            description=data.get('description', ''),
            dashboard_type=data.get('dashboard_type', 'custom'),
            widgets=data.get('widgets', []),
            layout=data.get('layout', {}),
            owner_user_id=g.user_id,
            is_public=data.get('is_public', False),
            auto_refresh_seconds=data.get('auto_refresh_seconds', 300),
        )
        
        session.add(dashboard)
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 201
    
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>', methods=['GET'])
@require_tenant()
def get_dashboard(dashboard_id):
    """GET /api/dashboards/{dashboard_id} - Get dashboard details"""
    try:
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        # Update view count
        dashboard.view_count = (dashboard.view_count or 0) + 1
        dashboard.last_viewed_at = datetime.utcnow()
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>', methods=['PUT'])
@require_tenant()
def update_dashboard(dashboard_id):
    """
    PUT /api/dashboards/{dashboard_id}
    Update dashboard configuration
    """
    try:
        from analytics_models import Dashboard
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        # Update fields
        if 'name' in data:
            dashboard.name = data['name']
        if 'description' in data:
            dashboard.description = data['description']
        if 'widgets' in data:
            dashboard.widgets = data['widgets']
        if 'layout' in data:
            dashboard.layout = data['layout']
        if 'dashboard_type' in data:
            dashboard.dashboard_type = data['dashboard_type']
        if 'auto_refresh_seconds' in data:
            dashboard.auto_refresh_seconds = data['auto_refresh_seconds']
        if 'is_public' in data:
            dashboard.is_public = data['is_public']
        
        dashboard.updated_at = datetime.utcnow()
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 200
    
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>', methods=['DELETE'])
@require_tenant()
def delete_dashboard(dashboard_id):
    """DELETE /api/dashboards/{dashboard_id} - Delete dashboard"""
    try:
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        session.delete(dashboard)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Dashboard deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting dashboard: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Widget Management Endpoints
# ============================================================================

@dashboards_bp.route('/<dashboard_id>/widgets', methods=['GET'])
@require_tenant()
def get_dashboard_widgets(dashboard_id):
    """GET /api/dashboards/{dashboard_id}/widgets - Get all widgets"""
    try:
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        session.close()
        return jsonify({
            'dashboard_id': dashboard_id,
            'widgets': dashboard.widgets or [],
            'count': len(dashboard.widgets or []),
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting widgets: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>/widgets', methods=['POST'])
@require_tenant()
def add_widget(dashboard_id):
    """
    POST /api/dashboards/{dashboard_id}/widgets
    Add widget to dashboard
    
    Body: {
        "id": "widget-1",
        "type": "metric",
        "title": "Revenue",
        "metric_name": "total_revenue",
        "config": {...}
    }
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        if not dashboard.widgets:
            dashboard.widgets = []
        
        # Add widget with ID
        widget = {
            'id': data.get('id', str(uuid.uuid4())),
            'type': data.get('type', 'metric'),
            'title': data.get('title', ''),
            'metric_name': data.get('metric_name'),
            'config': data.get('config', {}),
        }
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.utcnow()
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 201
    
    except Exception as e:
        logger.error(f"Error adding widget: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>/widgets/<widget_id>', methods=['PUT'])
@require_tenant()
def update_widget(dashboard_id, widget_id):
    """
    PUT /api/dashboards/{dashboard_id}/widgets/{widget_id}
    Update specific widget
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        # Find and update widget
        widgets = dashboard.widgets or []
        widget_updated = False
        
        for widget in widgets:
            if widget.get('id') == widget_id:
                widget.update(data)
                widget_updated = True
                break
        
        if not widget_updated:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Widget not found'}), 404
        
        dashboard.widgets = widgets
        dashboard.updated_at = datetime.utcnow()
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 200
    
    except Exception as e:
        logger.error(f"Error updating widget: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>/widgets/<widget_id>', methods=['DELETE'])
@require_tenant()
def delete_widget(dashboard_id, widget_id):
    """DELETE /api/dashboards/{dashboard_id}/widgets/{widget_id}"""
    try:
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        # Remove widget
        widgets = [w for w in (dashboard.widgets or []) if w.get('id') != widget_id]
        
        if len(widgets) == len(dashboard.widgets or []):
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Widget not found'}), 404
        
        dashboard.widgets = widgets
        dashboard.updated_at = datetime.utcnow()
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 200
    
    except Exception as e:
        logger.error(f"Error deleting widget: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Dashboard Sharing Endpoints
# ============================================================================

@dashboards_bp.route('/<dashboard_id>/share', methods=['POST'])
@require_tenant()
def share_dashboard(dashboard_id):
    """
    POST /api/dashboards/{dashboard_id}/share
    Share dashboard with users or groups
    
    Body: {
        "users": ["user-1", "user-2"],
        "groups": ["group-1"],
        "is_public": false
    }
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        if 'is_public' in data:
            dashboard.is_public = data['is_public']
        
        if 'users' in data:
            dashboard.shared_with_users = data['users']
        
        if 'groups' in data:
            dashboard.shared_with_groups = data['groups']
        
        dashboard.updated_at = datetime.utcnow()
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 200
    
    except Exception as e:
        logger.error(f"Error sharing dashboard: {e}")
        return jsonify({'error': str(e)}), 500


@dashboards_bp.route('/<dashboard_id>/pin', methods=['POST'])
@require_tenant()
def pin_dashboard(dashboard_id):
    """POST /api/dashboards/{dashboard_id}/pin - Pin/unpin dashboard"""
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        dashboard.is_pinned = data.get('is_pinned', not dashboard.is_pinned)
        session.commit()
        
        result = dashboard.to_dict()
        session.close()
        
        return jsonify({'success': True, 'dashboard': result}), 200
    
    except Exception as e:
        logger.error(f"Error pinning dashboard: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Dashboard Data Refresh
# ============================================================================

@dashboards_bp.route('/<dashboard_id>/refresh', methods=['POST'])
@require_tenant()
def refresh_dashboard_data(dashboard_id):
    """POST /api/dashboards/{dashboard_id}/refresh - Refresh dashboard data"""
    try:
        session = current_app.SessionLocal()
        
        dashboard = get_dashboard_or_404(session, dashboard_id, g.tenant_id)
        if not dashboard:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Dashboard not found'}), 404
        
        dashboard.last_refreshed_at = datetime.utcnow()
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Dashboard refresh initiated',
            'dashboard_id': dashboard_id,
        }), 202
    
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Dashboard Templates
# ============================================================================

@dashboards_bp.route('/templates', methods=['GET'])
@require_tenant()
def get_dashboard_templates():
    """GET /api/dashboards/templates - Get available dashboard templates"""
    try:
        templates = {
            'executive': {
                'name': 'Executive Dashboard',
                'description': 'High-level business metrics',
                'widgets': [
                    {'type': 'metric', 'title': 'Revenue', 'metric_name': 'total_revenue'},
                    {'type': 'metric', 'title': 'Growth Rate', 'metric_name': 'growth_rate'},
                    {'type': 'chart', 'title': 'Revenue Trend'},
                ]
            },
            'operational': {
                'name': 'Operational Dashboard',
                'description': 'System performance and operational metrics',
                'widgets': [
                    {'type': 'metric', 'title': 'Uptime', 'metric_name': 'uptime_percent'},
                    {'type': 'metric', 'title': 'Error Rate', 'metric_name': 'error_rate'},
                ]
            },
            'technical': {
                'name': 'Technical Dashboard',
                'description': 'Detailed technical metrics',
                'widgets': [
                    {'type': 'metric', 'title': 'Response Time (p99)', 'metric_name': 'response_time_p99'},
                    {'type': 'chart', 'title': 'Request Rate'},
                ]
            }
        }
        
        return jsonify({
            'templates': templates,
            'count': len(templates),
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500
