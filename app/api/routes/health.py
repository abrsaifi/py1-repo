"""
Health check and monitoring endpoints for application status.
Provides system metrics, database health, and performance indicators.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone
import os
import sqlite3
from typing import Dict, Any
import logging

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)

bp = Blueprint('api_health', __name__)


@bp.route('/health', methods=['GET'])
def health():
    """Basic health check endpoint."""
    return jsonify({'status': 'ok'})


@bp.route('/health/status', methods=['GET'])
def get_status() -> tuple:
    """Get overall application status."""
    try:
        status = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'healthy',
            'version': '1.0.0',
            'components': {
                'database': check_database_health(),
                'system': check_system_health(),
                'conversions': check_conversion_health(),
            }
        }
        
        # Determine overall status
        component_statuses = [v.get('status', 'unknown') for v in status['components'].values()]
        if 'unhealthy' in component_statuses:
            status['status'] = 'unhealthy'
        elif 'degraded' in component_statuses:
            status['status'] = 'degraded'
        
        http_code = 200 if status['status'] == 'healthy' else 503
        return jsonify(status), http_code
        
    except Exception as e:
        logger.error(f'Health check error: {str(e)}', exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@bp.route('/health/live', methods=['GET'])
def liveness_probe() -> tuple:
    """Kubernetes liveness probe - app is running."""
    return jsonify({'status': 'alive'}), 200


@bp.route('/health/ready', methods=['GET'])
def readiness_probe() -> tuple:
    """Kubernetes readiness probe - app is ready to serve requests."""
    try:
        # Check critical components
        check_database_health()
        return jsonify({'status': 'ready'}), 200
    except Exception:
        return jsonify({'status': 'not_ready'}), 503


@bp.route('/health/metrics', methods=['GET'])
def get_metrics() -> tuple:
    """Get application metrics for monitoring."""
    try:
        metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'service': 'docpro',
            'system': check_system_health(),
            'database': {
                'status': check_database_health().get('status')
            }
        }
        return jsonify(metrics), 200
    except Exception as e:
        logger.error(f'Metrics endpoint error: {str(e)}')
        return jsonify({'error': 'Failed to gather metrics'}), 500


def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and status."""
    try:
        history_db = 'conversion_history.db'
        
        if os.path.exists(history_db):
            size = os.path.getsize(history_db)
            
            # Quick connectivity test
            with sqlite3.connect(history_db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM history LIMIT 1')
                count = cursor.fetchone()[0]
            
            return {
                'status': 'healthy',
                'type': 'sqlite',
                'size_bytes': size,
                'records': count
            }
        else:
            return {
                'status': 'degraded',
                'message': 'Database file not found'
            }
    except Exception as e:
        logger.error(f'Database health check failed: {str(e)}')
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_system_health() -> Dict[str, Any]:
    """Check system resources."""
    try:
        if psutil is None:
            return {
                'status': 'unknown',
                'message': 'psutil not available'
            }
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = 'healthy'
        if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
            status = 'degraded'
        if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
            status = 'unhealthy'
        
        return {
            'status': status,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available // (1024 * 1024),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free // (1024 * 1024 * 1024),
        }
    except Exception as e:
        logger.error(f'System health check failed: {str(e)}')
        return {
            'status': 'unknown',
            'error': str(e)
        }


def check_conversion_health() -> Dict[str, Any]:
    """Check conversion system health."""
    try:
        # Check if conversion utilities are available
        from PIL import Image
        from docx import Document
        import openpyxl
        from pptx import Presentation
        
        return {
            'status': 'healthy',
            'capabilities': {
                'image_processing': True,
                'document_conversion': True,
                'excel_processing': True,
                'presentation_processing': True,
            }
        }
    except ImportError as e:
        logger.warning(f'Conversion health check warning: {str(e)}')
        return {
            'status': 'degraded',
            'error': f'Missing dependencies: {str(e)}'
        }
    except Exception as e:
        logger.error(f'Conversion health check failed: {str(e)}')
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

