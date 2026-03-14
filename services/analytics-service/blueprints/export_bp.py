"""
Export Blueprint
Endpoints for exporting analytics data in various formats
"""

from flask import Blueprint, request, jsonify, g, send_file, current_app
from datetime import datetime, timezone
from functools import wraps
import uuid
import logging
import json

export_bp = Blueprint('export', __name__, url_prefix='/export')
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
# Metrics Export
# ============================================================================

@export_bp.route('/metrics', methods=['POST'])
@require_tenant()
def export_metrics():
    """
    POST /api/export/metrics
    Export metrics data in specified format
    
    Body: {
        "format": "csv",
        "metric_names": ["response_time", "error_rate"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "service_name": "auth-service"
    }
    """
    try:
        data = request.get_json() or {}
        export_format = data.get('format', 'csv')
        
        if export_format not in ['csv', 'json', 'xlsx']:
            return jsonify({'error': 'Bad Request', 'message': 'Invalid format'}), 400
        
        # Create export task
        task_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'message': 'Export task started',
            'task_id': task_id,
            'format': export_format,
            'download_url': f'/api/export/download/{task_id}',
            'status_url': f'/api/export/status/{task_id}',
        }), 202
    
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        return jsonify({'error': str(e)}), 500


@export_bp.route('/dashboards', methods=['POST'])
@require_tenant()
def export_dashboards():
    """
    POST /api/export/dashboards
    Export dashboard definitions
    
    Body: {
        "dashboard_ids": ["id1", "id2"],
        "format": "json"
    }
    """
    try:
        data = request.get_json() or {}
        dashboard_ids = data.get('dashboard_ids', [])
        export_format = data.get('format', 'json')
        
        if not dashboard_ids:
            return jsonify({'error': 'Bad Request', 'message': 'dashboard_ids required'}), 400
        
        task_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'message': 'Dashboard export started',
            'task_id': task_id,
            'dashboard_count': len(dashboard_ids),
            'download_url': f'/api/export/download/{task_id}',
        }), 202
    
    except Exception as e:
        logger.error(f"Error exporting dashboards: {e}")
        return jsonify({'error': str(e)}), 500


@export_bp.route('/reports', methods=['POST'])
@require_tenant()
def export_reports():
    """
    POST /api/export/reports
    Export reports
    
    Body: {
        "report_ids": ["id1", "id2"],
        "format": "zip"
    }
    """
    try:
        data = request.get_json() or {}
        report_ids = data.get('report_ids', [])
        export_format = data.get('format', 'zip')
        
        if not report_ids:
            return jsonify({'error': 'Bad Request', 'message': 'report_ids required'}), 400
        
        task_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'message': 'Reports export started',
            'task_id': task_id,
            'report_count': len(report_ids),
            'download_url': f'/api/export/download/{task_id}',
        }), 202
    
    except Exception as e:
        logger.error(f"Error exporting reports: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Export Status and Download
# ============================================================================

@export_bp.route('/status/<task_id>', methods=['GET'])
@require_tenant()
def get_export_status(task_id):
    """
    GET /api/export/status/{task_id}
    Get export task status
    """
    try:
        # In real implementation, would query task queue/cache
        status = {
            'task_id': task_id,
            'status': 'completed',  # pending, processing, completed, failed
            'progress_percent': 100,
            'items_processed': 100,
            'total_items': 100,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'completed_at': datetime.now(timezone.utc).isoformat(),
        }
        
        return jsonify(status), 200
    
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        return jsonify({'error': str(e)}), 500


@export_bp.route('/download/<task_id>', methods=['GET'])
@require_tenant()
def download_export(task_id):
    """
    GET /api/export/download/{task_id}
    Download exported data file
    """
    try:
        # In real implementation, would stream file from S3 or local storage
        return jsonify({
            'download_url': f's3://exports/{task_id}.zip',
            'expires_in_seconds': 3600,
            'file_size_bytes': 1024000,
        }), 200
    
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Bulk Exports
# ============================================================================

@export_bp.route('/bulk', methods=['POST'])
@require_tenant()
def create_bulk_export():
    """
    POST /api/export/bulk
    Create comprehensive bulk export of all analytics
    
    Body: {
        "include": ["metrics", "dashboards", "reports", "alerts"],
        "format": "zip",
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-01-31"
        }
    }
    """
    try:
        data = request.get_json() or {}
        include = data.get('include', ['metrics', 'dashboards', 'reports'])
        export_format = data.get('format', 'zip')
        
        task_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'message': 'Bulk export started',
            'task_id': task_id,
            'items_to_export': len(include),
            'status_url': f'/api/export/status/{task_id}',
        }), 202
    
    except Exception as e:
        logger.error(f"Error creating bulk export: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Archive Management
# ============================================================================

@export_bp.route('/archives', methods=['GET'])
@require_tenant()
def list_export_archives():
    """
    GET /api/export/archives
    List previously created exports
    """
    try:
        archives = {
            'exports': [
                {
                    'task_id': 'task-001',
                    'created_at': '2024-01-15T10:30:00Z',
                    'format': 'zip',
                    'export_type': 'bulk',
                    'file_size_bytes': 5242880,
                    'expires_at': '2024-02-14T10:30:00Z',
                },
                {
                    'task_id': 'task-002',
                    'created_at': '2024-01-10T14:45:00Z',
                    'format': 'csv',
                    'export_type': 'metrics',
                    'file_size_bytes': 1048576,
                    'expires_at': '2024-02-09T14:45:00Z',
                },
            ],
            'count': 2,
        }
        
        return jsonify(archives), 200
    
    except Exception as e:
        logger.error(f"Error listing archives: {e}")
        return jsonify({'error': str(e)}), 500


@export_bp.route('/archives/<task_id>', methods=['DELETE'])
@require_tenant()
def delete_export_archive(task_id):
    """DELETE /api/export/archives/{task_id}"""
    try:
        return jsonify({
            'success': True,
            'message': 'Archive deleted',
            'task_id': task_id,
        }), 200
    
    except Exception as e:
        logger.error(f"Error deleting archive: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Advanced Exports
# ============================================================================

@export_bp.route('/scheduled', methods=['POST'])
@require_tenant()
def create_scheduled_export():
    """
    POST /api/export/scheduled
    Create scheduled recurring export
    
    Body: {
        "name": "Monthly Analytics Export",
        "include": ["metrics", "dashboards"],
        "format": "zip",
        "frequency": "monthly",
        "recipients": ["user@example.com"]
    }
    """
    try:
        data = request.get_json() or {}
        
        return jsonify({
            'success': True,
            'message': 'Scheduled export created',
            'name': data.get('name'),
            'frequency': data.get('frequency'),
            'next_run': '2024-02-01T00:00:00Z',
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating scheduled export: {e}")
        return jsonify({'error': str(e)}), 500


@export_bp.route('/formats', methods=['GET'])
@require_tenant()
def get_supported_formats():
    """GET /api/export/formats - Get supported export formats"""
    try:
        formats = {
            'formats': {
                'csv': {
                    'name': 'CSV',
                    'description': 'Comma-separated values',
                    'extension': 'csv',
                    'applicable_to': ['metrics', 'reports'],
                },
                'json': {
                    'name': 'JSON',
                    'description': 'JavaScript Object Notation',
                    'extension': 'json',
                    'applicable_to': ['metrics', 'dashboards', 'alerts', 'queries'],
                },
                'xlsx': {
                    'name': 'Excel',
                    'description': 'Microsoft Excel Workbook',
                    'extension': 'xlsx',
                    'applicable_to': ['metrics', 'reports'],
                },
                'pdf': {
                    'name': 'PDF',
                    'description': 'Portable Document Format',
                    'extension': 'pdf',
                    'applicable_to': ['reports', 'dashboards'],
                },
                'zip': {
                    'name': 'ZIP Archive',
                    'description': 'Compressed archive',
                    'extension': 'zip',
                    'applicable_to': ['bulk'],
                },
            },
            'count': 5,
        }
        
        return jsonify(formats), 200
    
    except Exception as e:
        logger.error(f"Error getting formats: {e}")
        return jsonify({'error': str(e)}), 500
