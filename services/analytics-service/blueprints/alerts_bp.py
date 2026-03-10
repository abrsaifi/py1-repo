"""
Alerts Blueprint
Endpoints for alert configuration, threshold management, and event tracking
"""

from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy.orm import Session
from datetime import datetime
from functools import wraps
import uuid
import logging



alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')
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


def get_alert_or_404(session, alert_id, tenant_id):
    """Helper to fetch alert by ID with tenant check"""
    from analytics_models import Alert
    
    alert = session.query(Alert).filter(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id
    ).first()
    
    return alert


# ============================================================================
# Alert CRUD Endpoints
# ============================================================================

@alerts_bp.route('', methods=['GET'])
@require_tenant()
def list_alerts():
    """
    GET /api/alerts?status=active&severity=critical&limit=50
    List alerts with filtering
    """
    try:
        from analytics_models import Alert
        
        status = request.args.get('status')
        severity = request.args.get('severity')
        limit = min(int(request.args.get('limit', 50)), 500)
        
        session = current_app.SessionLocal()
        query = session.query(Alert).filter(
            Alert.tenant_id == g.tenant_id
        )
        
        if status:
            query = query.filter(Alert.status == status)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
        
        result = {
            'alerts': [a.to_dict() for a in alerts],
            'count': len(alerts),
            'filters': {'status': status, 'severity': severity},
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('', methods=['POST'])
@require_tenant()
def create_alert():
    """
    POST /api/alerts
    Create new alert
    
    Body: {
        "metric_name": "error_rate",
        "condition_type": "threshold",
        "threshold_value": 5.0,
        "comparison_operator": ">",
        "severity": "critical",
        "notification_channels": ["email", "slack"],
        "recipients": ["user@example.com"]
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('metric_name'):
            return jsonify({'error': 'Bad Request', 'message': 'metric_name is required'}), 400
        
        session = current_app.SessionLocal()
        
        alert = Alert(
            id=str(uuid.uuid4()),
            tenant_id=g.tenant_id,
            metric_name=data.get('metric_name'),
            condition_type=data.get('condition_type', 'threshold'),
            threshold_value=data.get('threshold_value'),
            comparison_operator=data.get('comparison_operator', '>'),
            severity=data.get('severity', 'warning'),
            notification_channels=data.get('notification_channels', ['email']),
            recipients=data.get('recipients', []),
            is_active=True,
            created_by_user_id=g.user_id,
        )
        
        session.add(alert)
        session.commit()
        
        result = alert.to_dict()
        session.close()
        
        return jsonify({'success': True, 'alert': result}), 201
    
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('/<alert_id>', methods=['GET'])
@require_tenant()
def get_alert(alert_id):
    """GET /api/alerts/{alert_id} - Get alert details"""
    try:
        session = current_app.SessionLocal()
        
        alert = get_alert_or_404(session, alert_id, g.tenant_id)
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        result = alert.to_dict()
        session.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting alert: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('/<alert_id>', methods=['PUT'])
@require_tenant()
def update_alert(alert_id):
    """
    PUT /api/alerts/{alert_id}
    Update alert configuration
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        alert = get_alert_or_404(session, alert_id, g.tenant_id)
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        # Update fields
        if 'threshold_value' in data:
            alert.threshold_value = data['threshold_value']
        if 'comparison_operator' in data:
            alert.comparison_operator = data['comparison_operator']
        if 'severity' in data:
            alert.severity = data['severity']
        if 'notification_channels' in data:
            alert.notification_channels = data['notification_channels']
        if 'recipients' in data:
            alert.recipients = data['recipients']
        if 'is_active' in data:
            alert.is_active = data['is_active']
        
        session.commit()
        
        result = alert.to_dict()
        session.close()
        
        return jsonify({'success': True, 'alert': result}), 200
    
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('/<alert_id>', methods=['DELETE'])
@require_tenant()
def delete_alert(alert_id):
    """DELETE /api/alerts/{alert_id} - Delete alert"""
    try:
        session = current_app.SessionLocal()
        
        alert = get_alert_or_404(session, alert_id, g.tenant_id)
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        session.delete(alert)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Alert deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Alert Events Endpoints
# ============================================================================

@alerts_bp.route('/<alert_id>/events', methods=['GET'])
@require_tenant()
def list_alert_events(alert_id):
    """
    GET /api/alerts/{alert_id}/events
    Get alert trigger events
    """
    try:
        from analytics_models import AlertEvent
        
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        session = current_app.SessionLocal()
        
        # Verify alert exists
        from analytics_models import Alert
        alert = session.query(Alert).filter(
            Alert.id == alert_id,
            Alert.tenant_id == g.tenant_id
        ).first()
        
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        events = session.query(AlertEvent).filter(
            AlertEvent.alert_id == alert_id
        ).order_by(AlertEvent.triggered_at.desc()).limit(limit).all()
        
        result = {
            'alert_id': alert_id,
            'events': [e.to_dict() for e in events],
            'count': len(events),
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing alert events: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('/events/<event_id>/acknowledge', methods=['POST'])
@require_tenant()
def acknowledge_alert_event(event_id):
    """
    POST /api/alerts/events/{event_id}/acknowledge
    Acknowledge alert event
    
    Body: {
        "message": "Acknowledged - investigating"
    }
    """
    try:
        from analytics_models import AlertEvent
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        event = session.query(AlertEvent).filter(
            AlertEvent.id == event_id
        ).first()
        
        if not event:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Event not found'}), 404
        
        event.status = 'acknowledged'
        event.acknowledged_by = g.user_id
        event.acknowledged_at = datetime.utcnow()
        event.acknowledgment_message = data.get('message')
        
        session.commit()
        result = event.to_dict()
        session.close()
        
        return jsonify({'success': True, 'event': result}), 200
    
    except Exception as e:
        logger.error(f"Error acknowledging event: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('/events/<event_id>/resolve', methods=['POST'])
@require_tenant()
def resolve_alert_event(event_id):
    """
    POST /api/alerts/events/{event_id}/resolve
    Mark alert event as resolved
    
    Body: {
        "message": "Issue fixed",
        "auto_resolved": false
    }
    """
    try:
        from analytics_models import AlertEvent
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        event = session.query(AlertEvent).filter(
            AlertEvent.id == event_id
        ).first()
        
        if not event:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Event not found'}), 404
        
        event.status = 'resolved'
        event.resolved_by = g.user_id if not data.get('auto_resolved') else 'auto'
        event.resolved_at = datetime.utcnow()
        event.resolution_message = data.get('message')
        
        session.commit()
        result = event.to_dict()
        session.close()
        
        return jsonify({'success': True, 'event': result}), 200
    
    except Exception as e:
        logger.error(f"Error resolving event: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Alert Rules
# ============================================================================

@alerts_bp.route('/<alert_id>/rules', methods=['GET'])
@require_tenant()
def get_alert_rules(alert_id):
    """
    GET /api/alerts/{alert_id}/rules
    Get alert rule details
    """
    try:
        session = current_app.SessionLocal()
        
        alert = get_alert_or_404(session, alert_id, g.tenant_id)
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        rules = {
            'alert_id': alert_id,
            'condition': {
                'type': alert.condition_type,
                'metric_name': alert.metric_name,
                'threshold': alert.threshold_value,
                'operator': alert.comparison_operator,
            },
            'notifications': {
                'channels': alert.notification_channels,
                'recipients': alert.recipients,
                'severity': alert.severity,
            }
        }
        
        session.close()
        return jsonify(rules), 200
    
    except Exception as e:
        logger.error(f"Error getting rules: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Alert Status Management
# ============================================================================

@alerts_bp.route('/<alert_id>/enable', methods=['POST'])
@require_tenant()
def enable_alert(alert_id):
    """POST /api/alerts/{alert_id}/enable - Enable alert"""
    try:
        session = current_app.SessionLocal()
        
        alert = get_alert_or_404(session, alert_id, g.tenant_id)
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        alert.is_active = True
        session.commit()
        
        result = alert.to_dict()
        session.close()
        
        return jsonify({'success': True, 'alert': result}), 200
    
    except Exception as e:
        logger.error(f"Error enabling alert: {e}")
        return jsonify({'error': str(e)}), 500


@alerts_bp.route('/<alert_id>/disable', methods=['POST'])
@require_tenant()
def disable_alert(alert_id):
    """POST /api/alerts/{alert_id}/disable - Disable alert"""
    try:
        session = current_app.SessionLocal()
        
        alert = get_alert_or_404(session, alert_id, g.tenant_id)
        if not alert:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Alert not found'}), 404
        
        alert.is_active = False
        session.commit()
        
        result = alert.to_dict()
        session.close()
        
        return jsonify({'success': True, 'alert': result}), 200
    
    except Exception as e:
        logger.error(f"Error disabling alert: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Alert Summary
# ============================================================================

@alerts_bp.route('/summary', methods=['GET'])
@require_tenant()
def get_alerts_summary():
    """
    GET /api/alerts/summary
    Get summary of active and recent alerts
    """
    try:
        from analytics_models import Alert, AlertEvent, AlertStatus, AlertSeverity
        
        session = current_app.SessionLocal()
        
        # Get active alerts count
        active_count = session.query(Alert).filter(
            Alert.tenant_id == g.tenant_id,
            Alert.is_active == True
        ).count()
        
        # Get recent critical events
        recent_critical = session.query(AlertEvent).filter(
            AlertEvent.severity == 'critical'
        ).order_by(AlertEvent.triggered_at.desc()).limit(10).all()
        
        # Count by status
        active_events = session.query(AlertEvent).filter(
            AlertEvent.status == 'active'
        ).count()
        
        session.close()
        
        return jsonify({
            'active_alerts': active_count,
            'active_events': active_events,
            'recent_critical': [e.to_dict() for e in recent_critical],
            'summary': {
                'total_active': active_count,
                'total_events': active_events,
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({'error': str(e)}), 500
