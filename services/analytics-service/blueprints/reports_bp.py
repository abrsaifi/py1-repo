"""
Reports Blueprint
Endpoints for report scheduling, generation, retrieval, and export
"""

from flask import Blueprint, request, jsonify, g, send_file, current_app
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from functools import wraps
import uuid
import logging

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')
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


def get_report_or_404(session, report_id, tenant_id):
    """Helper to fetch report by ID with tenant check"""
    from analytics_models import Report
    
    report = session.query(Report).filter(
        Report.id == report_id,
        Report.tenant_id == tenant_id
    ).first()
    
    return report


# ============================================================================
# Report CRUD Endpoints
# ============================================================================

@reports_bp.route('', methods=['GET'])
@require_tenant()
def list_reports():
    """
    GET /api/reports?status=completed&report_type=summary&limit=50
    List reports with filtering
    """
    try:
        from analytics_models import Report, ReportStatus
        
        status = request.args.get('status')
        report_type = request.args.get('report_type')
        limit = min(int(request.args.get('limit', 50)), 500)
        
        session = current_app.SessionLocal()
        query = session.query(Report).filter(
            Report.tenant_id == g.tenant_id
        )
        
        if status:
            query = query.filter(Report.status == status)
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        reports = query.order_by(Report.created_at.desc()).limit(limit).all()
        
        result = {
            'reports': [r.to_dict() for r in reports],
            'count': len(reports),
            'filters': {
                'status': status,
                'report_type': report_type,
            },
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('', methods=['POST'])
@require_tenant()
def create_report():
    """
    POST /api/reports
    Create new report
    
    Body: {
        "name": "Monthly Revenue Report",
        "description": "Revenue and MRR trends",
        "report_type": "summary",
        "sections": ["revenue", "growth", "churn"],
        "metrics_included": ["mrr", "arr", "growth_rate"],
        "is_scheduled": true,
        "schedule_frequency": "monthly"
    }
    """
    try:
        from analytics_models import Report, ReportStatus
        
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({'error': 'Bad Request', 'message': 'name is required'}), 400
        
        session = current_app.SessionLocal()
        
        report = Report(
            id=str(uuid.uuid4()),
            tenant_id=g.tenant_id,
            name=data.get('name'),
            description=data.get('description', ''),
            report_type=data.get('report_type', 'summary'),
            sections=data.get('sections', []),
            metrics_included=data.get('metrics_included', []),
            charts_included=data.get('charts_included', []),
            created_by_user_id=g.user_id,
            is_scheduled=data.get('is_scheduled', False),
            schedule_frequency=data.get('schedule_frequency'),
            status='pending',
            recipients=data.get('recipients', []),
        )
        
        session.add(report)
        session.commit()
        
        result = report.to_dict()
        session.close()
        
        return jsonify({'success': True, 'report': result}), 201
    
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/<report_id>', methods=['GET'])
@require_tenant()
def get_report(report_id):
    """GET /api/reports/{report_id} - Get report details"""
    try:
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        result = report.to_dict()
        session.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/<report_id>', methods=['PUT'])
@require_tenant()
def update_report(report_id):
    """
    PUT /api/reports/{report_id}
    Update report configuration
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        # Update fields
        if 'name' in data:
            report.name = data['name']
        if 'description' in data:
            report.description = data['description']
        if 'sections' in data:
            report.sections = data['sections']
        if 'metrics_included' in data:
            report.metrics_included = data['metrics_included']
        if 'is_scheduled' in data:
            report.is_scheduled = data['is_scheduled']
        if 'schedule_frequency' in data:
            report.schedule_frequency = data['schedule_frequency']
        if 'recipients' in data:
            report.recipients = data['recipients']
        
        report.updated_at = datetime.now(timezone.utc)
        session.commit()
        
        result = report.to_dict()
        session.close()
        
        return jsonify({'success': True, 'report': result}), 200
    
    except Exception as e:
        logger.error(f"Error updating report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/<report_id>', methods=['DELETE'])
@require_tenant()
def delete_report(report_id):
    """DELETE /api/reports/{report_id} - Delete report"""
    try:
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        session.delete(report)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Report deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting report: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Report Generation Endpoints
# ============================================================================

@reports_bp.route('/<report_id>/generate', methods=['POST'])
@require_tenant()
def generate_report(report_id):
    """
    POST /api/reports/{report_id}/generate
    Trigger report generation
    
    Body: {
        "format": "pdf",
        "send_email": true
    }
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        # Update status
        report.status = 'generating'
        report.generation_count = (report.generation_count or 0) + 1
        session.commit()
        
        result = report.to_dict()
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Report generation started',
            'report': result,
        }), 202
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/<report_id>/download', methods=['GET'])
@require_tenant()
def download_report(report_id):
    """
    GET /api/reports/{report_id}/download
    Download report file
    """
    try:
        from analytics_models import ReportStatus
        
        file_format = request.args.get('format', 'pdf')
        
        session = current_app.SessionLocal()
        report = get_report_or_404(session, report_id, g.tenant_id)
        
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        if report.status != 'completed':
            session.close()
            return jsonify({
                'error': 'Bad Request',
                'message': 'Report is not ready for download',
                'status': report.status,
            }), 400
        
        # Simulate download URL
        download_url = f's3://reports/{report_id}.{file_format}'
        
        report.download_count = (report.download_count or 0) + 1
        session.commit()
        session.close()
        
        return jsonify({
            'download_url': download_url,
            'format': file_format,
            'expires_in_seconds': 3600,
            'file_size_bytes': report.file_size_bytes or 0,
        }), 200
    
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/<report_id>/schedule', methods=['POST'])
@require_tenant()
def schedule_report(report_id):
    """
    POST /api/reports/{report_id}/schedule
    Schedule report for automatic generation
    
    Body: {
        "frequency": "daily",
        "recipients": ["user@example.com"],
        "time_of_day": "09:00",
        "enabled": true
    }
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        report.is_scheduled = data.get('enabled', True)
        report.schedule_frequency = data.get('frequency', 'daily')
        report.recipients = data.get('recipients', [])
        
        if report.is_scheduled and report.schedule_frequency:
            # Calculate next generation time
            freq = report.schedule_frequency
            now = datetime.now(timezone.utc)
            
            if freq == 'daily':
                report.next_generation_at = now + timedelta(days=1)
            elif freq == 'weekly':
                report.next_generation_at = now + timedelta(weeks=1)
            elif freq == 'monthly':
                report.next_generation_at = now + timedelta(days=30)
        
        session.commit()
        
        result = report.to_dict()
        session.close()
        
        return jsonify({'success': True, 'report': result}), 200
    
    except Exception as e:
        logger.error(f"Error scheduling report: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Report History Endpoints
# ============================================================================

@reports_bp.route('/<report_id>/history', methods=['GET'])
@require_tenant()
def get_report_generation_history(report_id):
    """
    GET /api/reports/{report_id}/history
    Get report generation history
    """
    try:
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        # In real implementation, would query separate history table
        history = {
            'report_id': report_id,
            'generations': [
                {
                    'generated_at': report.last_generated_at.isoformat() if report.last_generated_at else None,
                    'status': report.status,
                    'file_size_bytes': report.file_size_bytes,
                }
            ],
            'total_generations': report.generation_count or 0,
        }
        
        session.close()
        
        return jsonify(history), 200
    
    except Exception as e:
        logger.error(f"Error getting report history: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Report Templates
# ============================================================================

@reports_bp.route('/templates', methods=['GET'])
@require_tenant()
def get_report_templates():
    """GET /api/reports/templates - Get available report templates"""
    try:
        templates = {
            'summary': {
                'name': 'Summary Report',
                'description': 'High-level business summary',
                'sections': ['revenue', 'growth', 'metrics'],
                'metrics': ['mrr', 'arr', 'growth_rate', 'churn_rate'],
            },
            'detailed': {
                'name': 'Detailed Report',
                'description': 'Comprehensive analysis',
                'sections': ['revenue', 'customers', 'product', 'churn'],
                'metrics': [
                    'mrr', 'arr', 'ltv', 'cac', 'nrr',
                    'total_customers', 'churn_rate',
                    'dau', 'wau', 'mau'
                ],
            },
            'executive': {
                'name': 'Executive Report',
                'description': 'C-level focused metrics',
                'sections': ['highlights', 'revenue', 'growth', 'risks'],
                'metrics': ['mrr', 'growth_rate', 'ltv_cac_ratio', 'churn_rate'],
            },
            'operational': {
                'name': 'Operational Report',
                'description': 'Service and performance metrics',
                'sections': ['system_health', 'performance', 'errors'],
                'metrics': ['uptime', 'error_rate', 'response_time', 'throughput'],
            },
        }
        
        return jsonify({
            'templates': templates,
            'count': len(templates),
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Report Exports
# ============================================================================

@reports_bp.route('/export', methods=['POST'])
@require_tenant()
def export_reports():
    """
    POST /api/reports/export
    Export multiple reports
    
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
        
        if export_format not in ['zip', 'json']:
            return jsonify({'error': 'Bad Request', 'message': 'Invalid format'}), 400
        
        return jsonify({
            'message': 'Export initiated',
            'report_count': len(report_ids),
            'format': export_format,
            'download_url': f'/api/reports/export/download?task_id=task-123',
        }), 202
    
    except Exception as e:
        logger.error(f"Error exporting reports: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Report Sharing
# ============================================================================

@reports_bp.route('/<report_id>/share', methods=['POST'])
@require_tenant()
def share_report(report_id):
    """
    POST /api/reports/{report_id}/share
    Share report with users
    
    Body: {
        "users": ["user1@example.com"],
        "groups": ["analytics"],
        "send_notification": true
    }
    """
    try:
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        report = get_report_or_404(session, report_id, g.tenant_id)
        if not report:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Report not found'}), 404
        
        # Update sharing
        if 'users' in data:
            report.recipients = data['users']
        
        session.commit()
        result = report.to_dict()
        session.close()
        
        return jsonify({'success': True, 'report': result}), 200
    
    except Exception as e:
        logger.error(f"Error sharing report: {e}")
        return jsonify({'error': str(e)}), 500
