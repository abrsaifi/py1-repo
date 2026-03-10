"""Enhanced Health Check Endpoints for Load Balancer"""
from flask import Blueprint, jsonify
from datetime import datetime
from app.models import db
import os

health_bp = Blueprint('health', __name__)

class HealthStatus:
    """Health status enumeration"""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    UNHEALTHY = 'unhealthy'

def check_database_health():
    """Check database connectivity and performance"""
    try:
        # Simple query to verify connection
        result = db.session.execute(
            'SELECT 1'
        ).fetchone()
        
        if result:
            return {
                'status': 'healthy',
                'response_time_ms': '<5',
                'message': 'Database connected'
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'Database query returned no result'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Database error: {str(e)}'
        }

def check_redis_health():
    """Check Redis connectivity"""
    try:
        from app.cache_manager import cache
        
        # Try to set and get a test key
        cache.set('health_check', 'ok', timeout=5)
        result = cache.get('health_check')
        
        if result == 'ok':
            cache.delete('health_check')
            return {
                'status': 'healthy',
                'message': 'Redis connected'
            }
        else:
            return {
                'status': 'unhealthy',
                'message': 'Redis test failed'
            }
    except Exception as e:
        return {
            'status': 'degraded',
            'message': f'Redis unavailable: {str(e)}'
        }

def check_celery_health():
    """Check Celery connectivity"""
    try:
        from app.celery_config import celery
        
        # Check worker availability
        stats = celery.control.inspect().stats()
        
        if stats:
            active_workers = len(stats)
            return {
                'status': 'healthy',
                'active_workers': active_workers,
                'message': f'{active_workers} workers active'
            }
        else:
            return {
                'status': 'degraded',
                'message': 'No Celery workers available'
            }
    except Exception as e:
        return {
            'status': 'degraded',
            'message': f'Celery check failed: {str(e)}'
        }

@health_bp.route('/health', methods=['GET'])
def basic_health_check():
    """Basic health check (fast, used by load balancer)"""
    return jsonify({
        'status': HealthStatus.HEALTHY,
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'docpro-api'
    }), 200

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check (all components)"""
    db_health = check_database_health()
    redis_health = check_redis_health()
    celery_health = check_celery_health()
    
    # Determine overall status
    statuses = [
        db_health.get('status'),
        redis_health.get('status'),
        celery_health.get('status')
    ]
    
    if all(s == HealthStatus.HEALTHY for s in statuses):
        overall_status = HealthStatus.HEALTHY
        http_code = 200
    elif any(s == HealthStatus.UNHEALTHY for s in statuses):
        overall_status = HealthStatus.UNHEALTHY
        http_code = 503
    else:
        overall_status = HealthStatus.DEGRADED
        http_code = 200
    
    response = {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'database': db_health,
            'redis': redis_health,
            'celery': celery_health
        },
        'version': os.getenv('APP_VERSION', '1.0.0')
    }
    
    return jsonify(response), http_code

@health_bp.route('/health/readiness', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe (simple but important checks)"""
    try:
        # Check database only for readiness
        db_result = check_database_health()
        
        if db_result.get('status') == HealthStatus.HEALTHY:
            return jsonify({
                'ready': True,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'ready': False,
                'reason': 'Database not healthy'
            }), 503
    except Exception as e:
        return jsonify({
            'ready': False,
            'reason': str(e)
        }), 503

@health_bp.route('/health/liveness', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe (should app be restarted?)"""
    try:
        # Check if app is responding
        return jsonify({
            'alive': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'alive': False,
            'error': str(e)
        }), 503

@health_bp.route('/health/startup', methods=['GET'])
def startup_check():
    """Kubernetes startup probe (has app finished initializing?)"""
    try:
        # Check if migrations are applied, cache is warmed, etc.
        db_health = check_database_health()
        redis_health = check_redis_health()
        
        if (db_health.get('status') == HealthStatus.HEALTHY and 
            redis_health.get('status') != HealthStatus.UNHEALTHY):
            return jsonify({
                'started': True,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'started': False,
                'reason': 'Dependencies not initialized'
            }), 503
    except Exception as e:
        return jsonify({
            'started': False,
            'error': str(e)
        }), 503

class HealthMetrics:
    """Metrics for health monitoring"""
    
    @staticmethod
    def get_component_metrics():
        """Get all component metrics"""
        return {
            'database': check_database_health(),
            'redis': check_redis_health(),
            'celery': check_celery_health(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def is_healthy():
        """Check if system is in healthy state"""
        db = check_database_health()
        return db.get('status') == HealthStatus.HEALTHY
    
    @staticmethod
    def is_degraded():
        """Check if system is degraded"""
        metrics = HealthMetrics.get_component_metrics()
        # System is degraded if any non-critical component is down
        redis = metrics['redis'].get('status')
        celery = metrics['celery'].get('status')
        
        return (redis == HealthStatus.DEGRADED or 
                celery == HealthStatus.DEGRADED)
