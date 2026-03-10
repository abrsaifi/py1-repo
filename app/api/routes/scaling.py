"""
Auto-Scaling API Routes
Provides endpoints for monitoring and managing auto-scaling behavior
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging

bp = Blueprint('scaling', __name__, url_prefix='/api/scaling')
logger = logging.getLogger(__name__)


@bp.route('/status', methods=['GET'])
def get_scaling_status():
    """
    Get current scaling status and metrics
    Returns: Current replica count, metrics, and recent scaling decisions
    """
    try:
        from ..autoscaling_manager import evaluate_scaling
        
        status = evaluate_scaling()
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            **status
        }), 200
    except Exception as e:
        logger.error(f"Failed to get scaling status: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/policy', methods=['GET'])
def get_scaling_policy():
    """
    Get current scaling policy
    Returns: Policy name, triggers, thresholds, min/max replicas
    """
    try:
        from flask import current_app
        
        manager = current_app.config.get('AUTOSCALING_MANAGER')
        if not manager:
            return jsonify({'error': 'Auto-scaling not initialized'}), 503
        
        policy = manager.policy
        return jsonify({
            'status': 'ok',
            'policy': {
                'name': policy.name,
                'enabled': policy.enabled,
                'min_replicas': policy.min_replicas,
                'max_replicas': policy.max_replicas,
                'scale_up_increment': policy.scale_up_increment,
                'scale_down_decrement': policy.scale_down_decrement,
                'triggers': [
                    {
                        'metric': trigger.metric.value,
                        'upper_bound': trigger.upper_bound,
                        'lower_bound': trigger.lower_bound,
                        'evaluation_periods': trigger.evaluation_periods,
                        'cooldown_seconds': trigger.cooldown_seconds,
                    }
                    for trigger in policy.triggers
                ]
            }
        }), 200
    except Exception as e:
        logger.error(f"Failed to get scaling policy: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/policy', methods=['POST'])
def change_scaling_policy():
    """
    Change the current scaling policy
    Requires: policy_name in request body (aggressive, balanced, conservative)
    Returns: Updated policy details
    Requires authorization
    """
    try:
        from flask import current_app
        from ..middleware.auth import auth_required, require_scope
        
        # Check authorization
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized - admin access required'}), 403
        
        data = request.get_json()
        policy_name = data.get('policy_name', '').lower()
        
        from ..autoscaling_manager import (
            get_autoscaling_manager,
            ScalingPolicies
        )
        
        manager = get_autoscaling_manager()
        
        # Map policy name to policy object
        policies = {
            'aggressive': ScalingPolicies.AGGRESSIVE,
            'balanced': ScalingPolicies.BALANCED,
            'conservative': ScalingPolicies.CONSERVATIVE,
        }
        
        if policy_name not in policies:
            return jsonify({
                'error': f'Unknown policy: {policy_name}',
                'available_policies': list(policies.keys())
            }), 400
        
        manager.policy = policies[policy_name]
        logger.info(f"Scaling policy changed to: {policy_name}")
        
        return jsonify({
            'status': 'ok',
            'message': f'Policy changed to {policy_name}',
            'policy': {
                'name': manager.policy.name,
                'min_replicas': manager.policy.min_replicas,
                'max_replicas': manager.policy.max_replicas,
            }
        }), 200
    except Exception as e:
        logger.error(f"Failed to change scaling policy: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/metrics', methods=['GET'])
def get_scaling_metrics():
    """
    Get current scaling metrics
    Returns: CPU, memory, request rate, latency, queue depth
    """
    try:
        from flask import current_app
        
        manager = current_app.config.get('AUTOSCALING_MANAGER')
        if not manager:
            return jsonify({'error': 'Auto-scaling not initialized'}), 503
        
        metrics_summary = manager.get_metrics_summary()
        return jsonify({
            'status': 'ok',
            **metrics_summary
        }), 200
    except Exception as e:
        logger.error(f"Failed to get scaling metrics: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/events', methods=['GET'])
def get_scaling_events():
    """
    Get scaling event history
    Query params: hours=24 (default), limit=100
    Returns: Array of scaling events with timestamps and metrics
    """
    try:
        from flask import current_app
        
        manager = current_app.config.get('AUTOSCALING_MANAGER')
        if not manager:
            return jsonify({'error': 'Auto-scaling not initialized'}), 503
        
        hours = int(request.args.get('hours', 24))
        limit = int(request.args.get('limit', 100))
        
        events = manager.get_scaling_history(hours=hours)
        
        # Convert to JSON-serializable format
        event_data = [
            {
                'timestamp': event.timestamp.isoformat(),
                'trigger_metric': event.trigger_metric.value,
                'metric_value': event.metric_value,
                'threshold': event.threshold,
                'action': event.action.value,
                'replicas_before': event.replicas_before,
                'replicas_after': event.replicas_after,
                'policy_name': event.policy_name,
                'reason': event.reason,
            }
            for event in events[-limit:]  # Limit results
        ]
        
        return jsonify({
            'status': 'ok',
            'count': len(event_data),
            'hours': hours,
            'events': event_data
        }), 200
    except Exception as e:
        logger.error(f"Failed to get scaling events: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/health', methods=['GET'])
def scaling_health():
    """
    Health check for auto-scaling system
    Returns: Status of metrics collection and scaling manager
    """
    try:
        from flask import current_app
        
        manager = current_app.config.get('AUTOSCALING_MANAGER')
        collector = current_app.config.get('METRICS_COLLECTOR')
        
        if not manager or not collector:
            return jsonify({
                'status': 'degraded',
                'message': 'Auto-scaling components not initialized'
            }), 503
        
        # Try to collect metrics
        snapshot = collector.collect_metrics()
        
        health_status = {
            'status': 'healthy',
            'components': {
                'manager': 'ok',
                'collector': 'ok',
                'policy': manager.policy.name,
            },
            'last_metric_collection': snapshot.timestamp.isoformat(),
            'current_metrics': {
                'cpu': f"{snapshot.cpu_utilization:.1f}%",
                'memory': f"{snapshot.memory_utilization:.1f}%",
                'request_rate': f"{snapshot.request_rate:.2f} req/sec",
                'response_time_ms': f"{snapshot.average_response_time:.1f} ms",
            }
        }
        
        return jsonify(health_status), 200
    except Exception as e:
        logger.error(f"Failed to get scaling health: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@bp.route('/forecast', methods=['GET'])
def get_scaling_forecast():
    """
    Get scaling recommendations based on current trends
    Returns: Predicted scaling actions if current trends continue
    """
    try:
        from flask import current_app
        
        manager = current_app.config.get('AUTOSCALING_MANAGER')
        if not manager:
            return jsonify({'error': 'Auto-scaling not initialized'}), 503
        
        collector = current_app.config.get('METRICS_COLLECTOR')
        if not collector:
            return jsonify({'error': 'Metrics collector not initialized'}), 503
        
        # Collect current snapshot
        snapshot = collector.collect_metrics()
        
        # Evaluate against policy
        trigger = manager.evaluate_metrics(snapshot)
        
        # Calculate recommended replicas
        recommended = manager.calculate_replicas(trigger)
        
        forecast = {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'current_replicas': manager.current_replicas,
            'recommended_replicas': recommended,
            'scaling_action': trigger.value,
            'reason': get_scaling_reason(manager, snapshot),
            'metrics': {
                'cpu': f"{snapshot.cpu_utilization:.1f}%",
                'memory': f"{snapshot.memory_utilization:.1f}%",
                'request_rate': f"{snapshot.request_rate:.2f} req/sec",
            }
        }
        
        if recommended != manager.current_replicas:
            forecast['change'] = recommended - manager.current_replicas
            forecast['summary'] = f"Scale {'up' if forecast['change'] > 0 else 'down'} by {abs(forecast['change'])} replicas"
        
        return jsonify(forecast), 200
    except Exception as e:
        logger.error(f"Failed to get scaling forecast: {e}")
        return jsonify({'error': str(e)}), 500


def verify_admin_access():
    """
    Verify that the current request has admin access
    Placeholder - integrate with your auth system
    """
    try:
        # Check for admin role or API key
        from flask import request, current_app
        
        # Check for Authorization header with admin scope
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            # Would validate JWT token here
            return True
        
        # Check for admin API key
        api_key = request.headers.get('X-API-Key')
        if api_key == current_app.config.get('ADMIN_API_KEY'):
            return True
        
        return False
    except:
        return False


def get_scaling_reason(manager, snapshot):
    """
    Generate a human-readable reason for scaling decision
    """
    policy = manager.policy
    reasons = []
    
    for trigger in policy.triggers:
        metric = trigger.metric.value
        if snapshot.cpu_utilization > trigger.upper_bound:
            reasons.append(f"CPU {snapshot.cpu_utilization:.1f}% > {trigger.upper_bound}%")
        elif snapshot.memory_utilization > trigger.upper_bound:
            reasons.append(f"Memory {snapshot.memory_utilization:.1f}% > {trigger.upper_bound}%")
    
    return " and ".join(reasons) if reasons else "Metrics within thresholds"


if __name__ == '__main__':
    print("Scaling routes module loaded successfully")
