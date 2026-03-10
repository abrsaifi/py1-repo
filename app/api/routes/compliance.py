"""
Compliance and Audit API Routes
Endpoints for GDPR operations, consent management, and compliance reporting
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from uuid import UUID
import logging

bp = Blueprint('compliance', __name__, url_prefix='/api/compliance')
logger = logging.getLogger(__name__)


@bp.route('/data/export', methods=['POST'])
def export_user_data():
    """
    Export all personal data for authenticated user (GDPR Article 15)
    Returns: Complete data export as JSON
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        manager = get_gdpr_manager(db.session)
        data_export = manager.export_user_data(UUID(user_id))
        
        return jsonify({
            'status': 'success',
            'message': 'Data export generated',
            'export_date': datetime.utcnow().isoformat(),
            'data': data_export
        }), 200
    except ValueError as e:
        logger.warning(f"Data export failed: {e}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        return jsonify({'error': 'Export generation failed'}), 500


@bp.route('/data/delete', methods=['POST'])
def request_data_deletion():
    """
    Request GDPR right-to-be-forgotten (Article 17)
    Returns: Deletion request ID for tracking
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json() or {}
        reason = data.get('reason', 'GDPR Article 17 - Right to be forgotten')
        
        manager = get_gdpr_manager(db.session)
        request_id = manager.request_data_deletion(
            user_id=UUID(user_id),
            reason=reason,
            request_by='user'
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Deletion request submitted',
            'request_id': str(request_id),
            'next_steps': [
                'Your deletion request has been submitted',
                'You will receive confirmation within 5 business days',
                'For urgent requests, contact support@example.com'
            ]
        }), 202
    except Exception as e:
        logger.error(f"Deletion request failed: {e}")
        return jsonify({'error': 'Request submission failed'}), 500


@bp.route('/data/deletion-status/<request_id>', methods=['GET'])
def check_deletion_status(request_id):
    """
    Check status of deletion request
    Returns: Current status and progress
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.models.compliance import DataDeletionRequest
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        req = db.session.query(DataDeletionRequest).filter_by(
            id=UUID(request_id),
            user_id=UUID(user_id)
        ).first()
        
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        
        return jsonify({
            'request_id': str(req.id),
            'status': req.status,
            'requested_at': req.requested_at.isoformat(),
            'approved_at': req.approved_at.isoformat() if req.approved_at else None,
            'completed_at': req.completed_at.isoformat() if req.completed_at else None,
            'records_deleted': req.total_records_deleted,
            'next_steps': get_deletion_next_steps(req.status)
        }), 200
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return jsonify({'error': 'Status check failed'}), 500


@bp.route('/consent/preferences', methods=['GET'])
def get_user_consents():
    """
    Get user's current consent preferences
    Returns: Object with all consent flags
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        manager = get_gdpr_manager(db.session)
        consents = manager.get_user_consents(UUID(user_id))
        
        return jsonify({
            'user_id': user_id,
            'consents': consents,
            'last_updated': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Failed to get consents: {e}")
        return jsonify({'error': 'Failed to retrieve consents'}), 500


@bp.route('/consent/preferences', methods=['POST'])
def update_user_consents():
    """
    Update user's consent preferences
    Body: {'data_processing': bool, 'marketing': bool, ...}
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No consent data provided'}), 400
        
        # Validate consent fields
        valid_fields = {'data_processing', 'marketing', 'analytics', 'third_party_sharing'}
        provided_fields = set(data.keys())
        if not provided_fields.issubset(valid_fields):
            return jsonify({'error': f'Invalid consent fields. Valid: {valid_fields}'}), 400
        
        # Add context
        data['ip_address'] = request.remote_addr
        data['user_agent'] = request.user_agent.string if request.user_agent else None
        
        manager = get_gdpr_manager(db.session)
        if manager.update_user_consent(UUID(user_id), **data):
            return jsonify({
                'status': 'success',
                'message': 'Consent preferences updated',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({'error': 'Failed to update consents'}), 500
    except Exception as e:
        logger.error(f"Failed to update consents: {e}")
        return jsonify({'error': 'Update failed'}), 500


@bp.route('/consent/withdraw', methods=['POST'])
def withdraw_consents():
    """
    Withdraw all consent (GDPR Article 7)
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        manager = get_gdpr_manager(db.session)
        if manager.withdraw_all_consent(UUID(user_id)):
            return jsonify({
                'status': 'success',
                'message': 'All consent withdrawn',
                'timestamp': datetime.utcnow().isoformat(),
                'note': 'We will stop processing your data as of this moment'
            }), 200
        else:
            return jsonify({'error': 'Failed to withdraw consent'}), 500
    except Exception as e:
        logger.error(f"Failed to withdraw consent: {e}")
        return jsonify({'error': 'Withdrawal failed'}), 500


@bp.route('/audit-log', methods=['GET'])
def get_user_audit_log():
    """
    Get audit log of actions affecting the user
    Query params: period_days=90, limit=100
    """
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_audit_logger
        from app.models import db
        
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        period_days = int(request.args.get('period_days', 90))
        limit = int(request.args.get('limit', 100))
        
        logger_inst = get_audit_logger(db.session)
        audit_trail = logger_inst.get_audit_trail(
            actor_id=UUID(user_id),
            period_days=period_days,
            limit=limit
        )
        
        return jsonify({
            'user_id': user_id,
            'period_days': period_days,
            'entries': audit_trail,
            'count': len(audit_trail)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        return jsonify({'error': 'Failed to retrieve audit log'}), 500


# Admin endpoints (require admin authorization)

@bp.route('/admin/deletions', methods=['GET'])
def list_deletion_requests():
    """
    List pending deletion requests (admin only)
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.models.compliance import DataDeletionRequest
        from app.models import db
        
        status = request.args.get('status', 'pending')
        limit = int(request.args.get('limit', 50))
        
        requests = db.session.query(DataDeletionRequest).filter_by(
            status=status
        ).order_by(DataDeletionRequest.requested_at.desc()).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'filter': {'status': status},
            'count': len(requests),
            'requests': [
                {
                    'id': str(r.id),
                    'user_id': str(r.user_id),
                    'requested_at': r.requested_at.isoformat(),
                    'status': r.status,
                    'approval_required': r.approval_required,
                }
                for r in requests
            ]
        }), 200
    except Exception as e:
        logger.error(f"Failed to list deletion requests: {e}")
        return jsonify({'error': 'Failed to list requests'}), 500


@bp.route('/admin/deletions/<request_id>/approve', methods=['POST'])
def approve_deletion(request_id):
    """
    Approve a pending deletion request (admin only)
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from flask_jwt_extended import get_jwt_identity
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        admin_id = get_jwt_identity()
        
        manager = get_gdpr_manager(db.session)
        if manager.approve_deletion_request(UUID(request_id), UUID(admin_id)):
            return jsonify({
                'status': 'success',
                'message': 'Deletion request approved',
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({'error': 'Failed to approve request'}), 500
    except Exception as e:
        logger.error(f"Failed to approve deletion: {e}")
        return jsonify({'error': 'Approval failed'}), 500


@bp.route('/admin/deletions/<request_id>/execute', methods=['POST'])
def execute_deletion(request_id):
    """
    Execute an approved deletion request (admin only)
    This will delete all user personal data
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.compliance_manager import get_gdpr_manager
        from app.models import db
        
        manager = get_gdpr_manager(db.session)
        success, deleted_count, error = manager.execute_data_deletion(UUID(request_id))
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Data deletion completed',
                'request_id': request_id,
                'records_deleted': deleted_count,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Deletion failed',
                'error': error
            }), 500
    except Exception as e:
        logger.error(f"Failed to execute deletion: {e}")
        return jsonify({'error': 'Execution failed'}), 500


@bp.route('/admin/reports/gdpr', methods=['GET'])
def get_gdpr_report():
    """
    Generate GDPR compliance report (admin only)
    Query params: period_days=30
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.compliance_manager import get_compliance_reporter
        from app.models import db
        
        period_days = int(request.args.get('period_days', 30))
        
        reporter = get_compliance_reporter(db.session)
        report = reporter.generate_gdpr_report(period_days=period_days)
        
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Failed to generate GDPR report: {e}")
        return jsonify({'error': 'Report generation failed'}), 500


@bp.route('/admin/reports/soc2', methods=['GET'])
def get_soc2_report():
    """
    Generate SOC2 compliance status report (admin only)
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.compliance_manager import get_compliance_reporter
        from app.models import db
        
        reporter = get_compliance_reporter(db.session)
        report = reporter.generate_soc2_report()
        
        return jsonify(report), 200
    except Exception as e:
        logger.error(f"Failed to generate SOC2 report: {e}")
        return jsonify({'error': 'Report generation failed'}), 500


@bp.route('/admin/audit-logs', methods=['GET'])
def search_audit_logs():
    """
    Search audit logs (admin only)
    Query params: resource_type, resource_id, actor_id, period_days=90, limit=100
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.compliance_manager import get_audit_logger
        from app.models import db
        
        resource_type = request.args.get('resource_type')
        resource_id = request.args.get('resource_id')
        actor_id = request.args.get('actor_id')
        period_days = int(request.args.get('period_days', 90))
        limit = int(request.args.get('limit', 100))
        
        logger_inst = get_audit_logger(db.session)
        audit_trail = logger_inst.get_audit_trail(
            resource_type=resource_type,
            resource_id=UUID(resource_id) if resource_id else None,
            actor_id=UUID(actor_id) if actor_id else None,
            period_days=period_days,
            limit=limit
        )
        
        return jsonify({
            'filters': {
                'resource_type': resource_type,
                'resource_id': resource_id,
                'actor_id': actor_id,
                'period_days': period_days,
            },
            'entries': audit_trail,
            'count': len(audit_trail)
        }), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid UUID format: {e}'}), 400
    except Exception as e:
        logger.error(f"Failed to search audit logs: {e}")
        return jsonify({'error': 'Search failed'}), 500


@bp.route('/admin/audit-cleanup', methods=['POST'])
def cleanup_expired_logs():
    """
    Delete expired audit logs according to retention policies (admin only)
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.compliance_manager import get_audit_logger
        from app.models import db
        
        logger_inst = get_audit_logger(db.session)
        deleted_count = logger_inst.cleanup_expired_logs()
        
        return jsonify({
            'status': 'success',
            'message': f'Cleanup completed',
            'logs_deleted': deleted_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")
        return jsonify({'error': 'Cleanup failed'}), 500


def verify_admin_access():
    """
    Verify that the current request has admin access
    Check for admin role or administrative API key
    """
    try:
        from flask_jwt_extended import get_jwt
        from app.models.user import User
        from app.models import db
        
        # Try JWT first
        jwt_data = get_jwt()
        if jwt_data and jwt_data.get('is_admin'):
            user_id = jwt_data.get('sub')
            user = db.session.query(User).filter_by(id=user_id).first()
            return user and user.is_admin
        
        # Check for admin API key
        api_key = request.headers.get('X-API-Key')
        if api_key == current_app.config.get('ADMIN_API_KEY'):
            return True
        
        return False
    except:
        return False


def get_deletion_next_steps(status: str) -> list:
    """Get next steps based on deletion status"""
    steps = {
        'pending': [
            'Your request is pending approval',
            'Support team will review within 5 business days',
            'You will receive confirmation email'
        ],
        'approved': [
            'Your request has been approved',
            'Data deletion will start within 24 hours',
            'You will receive confirmation when complete'
        ],
        'executing': [
            'Your data is being deleted',
            'This may take a few hours',
            'We will notify you when complete'
        ],
        'completed': [
            'Your data has been successfully deleted',
            'All personal information has been removed',
            'You can no longer log into your account'
        ],
        'failed': [
            'Data deletion encountered an error',
            'Please contact support@example.com',
            'Reference your request ID for faster assistance'
        ]
    }
    return steps.get(status, [])


if __name__ == '__main__':
    print("Compliance API routes module loaded successfully")
