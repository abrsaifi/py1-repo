"""
Disaster Recovery and Backup Management API Routes
Endpoints for backup management, recovery, monitoring, and testing
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging

bp = Blueprint('disaster_recovery', __name__, url_prefix='/api/disaster-recovery')
logger = logging.getLogger(__name__)


@bp.route('/backup/create', methods=['POST'])
def create_backup():
    """
    Trigger an immediate full database backup
    Returns: Backup file path and status
    Requires: admin authorization
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized - admin access required'}), 403
        
        from app.disaster_recovery_manager import get_backup_manager
        
        backup_manager = get_backup_manager()
        success, backup_file, error = backup_manager.create_full_backup()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Backup created',
                'backup_file': backup_file,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Backup failed',
                'error': error
            }), 500
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/backup/list', methods=['GET'])
def list_backups():
    """
    List recent backups
    Query params: limit=20
    Returns: Array of backup records with metadata
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.disaster_recovery_manager import get_backup_manager
        
        limit = int(request.args.get('limit', 20))
        
        backup_manager = get_backup_manager()
        backups = backup_manager.get_backup_history(limit=limit)
        
        return jsonify({
            'status': 'success',
            'count': len(backups),
            'backups': backups
        }), 200
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/backup/<backup_id>/verify', methods=['POST'])
def verify_backup(backup_id):
    """
    Verify backup integrity and optionally test restore
    Query params: test_restore=true (optional, runs slow)
    Returns: Verification results
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.disaster_recovery_manager import get_backup_manager
        
        test_restore = request.args.get('test_restore', 'false').lower() == 'true'
        
        backup_manager = get_backup_manager()
        backups = backup_manager.get_backup_history(limit=100)
        
        # Find backup by ID (timestamp)
        backup = next((b for b in backups if b['timestamp'] == backup_id), None)
        if not backup:
            return jsonify({'error': 'Backup not found'}), 404
        
        backup_file = backup.get('file')
        valid, info = backup_manager.verify_backup(backup_file, restore_to_temp=test_restore)
        
        return jsonify({
            'status': 'success' if valid else 'failed',
            'backup_id': backup_id,
            'valid': valid,
            'verification_info': info
        }), (200 if valid else 400)
    except Exception as e:
        logger.error(f"Backup verification failed: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/backup/cleanup', methods=['POST'])
def cleanup_old_backups():
    """
    Delete backups older than retention period
    Body: {retention_days: 30}
    Returns: Count of deleted backups and freed space
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json() or {}
        retention_days = data.get('retention_days', 30)
        
        # Validate retention period
        if retention_days < 7:
            return jsonify({'error': 'Minimum retention is 7 days'}), 400
        
        from app.disaster_recovery_manager import get_backup_manager
        
        backup_manager = get_backup_manager()
        deleted_count, freed_bytes = backup_manager.cleanup_old_backups(retention_days)
        
        return jsonify({
            'status': 'success',
            'message': f'Cleaned up {deleted_count} backups',
            'deleted_count': deleted_count,
            'freed_bytes': freed_bytes,
            'freed_mb': round(freed_bytes / (1024 * 1024), 2),
            'retention_days': retention_days,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/replication/status', methods=['GET'])
def get_replication_status():
    """
    Get current replication status
    Returns: Primary LSN, standby LSN, replication lag
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.disaster_recovery_manager import ReplicationMonitor
        from flask import current_app
        
        # Get database config
        primary_config = {
            'host': current_app.config.get('SQLALCHEMY_DATABASE_HOST', 'localhost'),
            'port': current_app.config.get('SQLALCHEMY_DATABASE_PORT', 5432),
            'user': current_app.config.get('SQLALCHEMY_DATABASE_USER', 'docpro'),
            'password': current_app.config.get('SQLALCHEMY_DATABASE_PASSWORD', ''),
            'database': current_app.config.get('SQLALCHEMY_DATABASE_NAME', 'docpro'),
        }
        
        # Standby config (would come from environment in production)
        standby_config = primary_config.copy()
        standby_config['host'] = current_app.config.get('STANDBY_HOST', 'localhost')
        standby_config['port'] = current_app.config.get('STANDBY_PORT', 5433)
        
        monitor = ReplicationMonitor(primary_config, standby_config)
        status = monitor.check_replication_status()
        
        return jsonify({
            'status': 'success',
            'replication': status
        }), 200
    except Exception as e:
        logger.error(f"Replication status check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'note': 'Standby may not be configured'
        }), 500


@bp.route('/recovery/options', methods=['GET'])
def get_recovery_options():
    """
    Get available recovery strategies and options
    Returns: List of recovery methods with estimated RTO
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.disaster_recovery_manager import get_backup_manager, RecoveryPlanner
        
        backup_manager = get_backup_manager()
        planner = RecoveryPlanner(current_app.config, backup_manager)
        
        options = planner.get_recovery_options()
        
        return jsonify({
            'status': 'success',
            'recovery_options': options
        }), 200
    except Exception as e:
        logger.error(f"Failed to get recovery options: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/recovery/rto-rpo', methods=['GET'])
def get_rto_rpo():
    """
    Get RTO (Recovery Time Objective) and RPO (Recovery Point Objective) estimates
    Returns: Estimated time to recover, point in time recovery capability
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.disaster_recovery_manager import get_backup_manager, RecoveryPlanner
        
        backup_manager = get_backup_manager()
        planner = RecoveryPlanner(current_app.config, backup_manager)
        
        rto_rpo = planner.estimate_rto_rpo()
        
        # Add compliance status
        compliant = (
            rto_rpo['target_rto_minutes'] >= rto_rpo['rto_estimate']['duration_minutes'] and
            rto_rpo['target_rpo_minutes'] >= rto_rpo['rpo_estimate']['duration_minutes']
        )
        
        return jsonify({
            'status': 'success',
            'rto_rpo': rto_rpo,
            'compliant': compliant,
            'compliance_note': 'Meets production targets' if compliant else 'BELOW TARGET - increase backup frequency'
        }), 200
    except Exception as e:
        logger.error(f"Failed to get RTO/RPO: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/recovery/plan/<recovery_type>', methods=['GET'])
def get_recovery_plan(recovery_type):
    """
    Get detailed recovery plan for specific scenario
    recovery_type: full_restore | pitr | standby_failover
    Returns: Step-by-step recovery procedure
    """
    try:
        if not verify_admin_access():
            return jsonify({'error': 'Unauthorized'}), 403
        
        recovery_plans = {
            'full_restore': {
                'title': 'Full Database Restore from Backup',
                'duration_minutes': 15,
                'data_loss_risk': 'Up to 24 hours',
                'steps': [
                    {'step': 1, 'action': 'Identify latest good backup'},
                    {'step': 2, 'action': 'Stop application servers'},
                    {'step': 3, 'action': 'Stop primary database'},
                    {'step': 4, 'action': 'Restore from backup: pg_restore -d docpro /backups/backup_*.sql'),
                    {'step': 5, 'action': 'Verify data integrity'},
                    {'step': 6, 'action': 'Restart application servers'},
                    {'step': 7, 'action': 'Verify application functionality'},
                ],
                'validation': [
                    'Check row counts match expectations',
                    'Run test queries',
                    'Verify application connects',
                ]
            },
            'pitr': {
                'title': 'Point-in-Time Recovery (PITR)',
                'duration_minutes': 30,
                'data_loss_risk': 'None - recover to exact point',
                'precondition': 'Requires WAL archives available',
                'steps': [
                    {'step': 1, 'action': 'Identify target recovery time'},
                    {'step': 2, 'action': 'Verify WAL archives exist for that time'},
                    {'step': 3, 'action': 'Stop application servers'},
                    {'step': 4, 'action': 'Stop primary database'},
                    {'step': 5, 'action': 'Restore from latest backup'},
                    {'step': 6, 'action': 'Set recovery_target_time in recovery.conf'},
                    {'step': 7, 'action': 'Start database (will replay WAL to target)'},
                    {'step': 8, 'action': 'Verify recovery time was reached'},
                ],
                'validation': [
                    'Check database recovered at exact time',
                    'Review transaction logs',
                ]
            },
            'standby_failover': {
                'title': 'Promote Standby to Primary',
                'duration_minutes': 1,
                'data_loss_risk': 'Minimal - only unwritten WAL',
                'precondition': 'Requires healthy standby server',
                'steps': [
                    {'step': 1, 'action': 'Verify primary is actually down'},
                    {'step': 2, 'action': 'On standby: pg_ctl promote -D /var/lib/postgresql/data'},
                    {'step': 3, 'action': 'Wait for standby to finish recovery'},
                    {'step': 4, 'action': 'Update application connection string (if static)'},
                    {'step': 5, 'action': 'Verify application connections succeed'},
                    {'step': 6, 'action': 'Set up new standby from promoted primary'},
                ],
                'validation': [
                    'Check standby is now accepting writes',
                    'Monitor replication to new standby',
                ]
            }
        }
        
        if recovery_type not in recovery_plans:
            return jsonify({
                'error': 'Unknown recovery type',
                'available_types': list(recovery_plans.keys())
            }), 400
        
        plan = recovery_plans[recovery_type]
        plan['recovery_type'] = recovery_type
        plan['timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify({
            'status': 'success',
            'plan': plan
        }), 200
    except Exception as e:
        logger.error(f"Failed to get recovery plan: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/health/backup-service', methods=['GET'])
def backup_service_health():
    """
    Check health of backup service
    Returns: Last backup time, backup health status
    """
    try:
        from app.disaster_recovery_manager import get_backup_manager
        from datetime import datetime, timedelta
        
        backup_manager = get_backup_manager()
        backups = backup_manager.get_backup_history(limit=1)
        
        if not backups:
            return jsonify({
                'status': 'unhealthy',
                'message': 'No backups found',
                'last_backup': None,
                'alert': 'CRITICAL - No backups exist'
            }), 503
        
        latest_backup = backups[0]
        backup_time = datetime.fromisoformat(latest_backup['timestamp'])
        age_hours = (datetime.utcnow() - backup_time).total_seconds() / 3600
        
        # Determine health based on backup age
        if age_hours < 24:
            health_status = 'healthy'
        elif age_hours < 48:
            health_status = 'degraded'
        else:
            health_status = 'unhealthy'
        
        return jsonify({
            'status': health_status,
            'last_backup': latest_backup['timestamp'],
            'backup_age_hours': round(age_hours, 1),
            'backup_file': latest_backup.get('file'),
            'backup_size_mb': round(latest_backup.get('size_bytes', 0) / (1024 * 1024), 2),
            'checksum': latest_backup.get('checksum', 'N/A')[:16] + '...',
            'next_backup_due': (backup_time + timedelta(hours=24)).isoformat(),
            'alert': 'Backup overdue - running 24h+ old' if health_status == 'unhealthy' else None
        }), 200
    except Exception as e:
        logger.error(f"Backup health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


def verify_admin_access():
    """Verify admin authorization for DR endpoints"""
    try:
        from flask_jwt_extended import get_jwt
        
        jwt_data = get_jwt()
        if jwt_data and jwt_data.get('is_admin'):
            return True
        
        # Check for admin API key
        api_key = request.headers.get('X-API-Key')
        if api_key == current_app.config.get('ADMIN_API_KEY'):
            return True
        
        return False
    except:
        return False


if __name__ == '__main__':
    print("Disaster recovery API routes module loaded successfully")
