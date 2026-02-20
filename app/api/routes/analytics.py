"""Analytics and monitoring endpoints"""
from flask import Blueprint, request, jsonify, current_app
from app.services.database import DatabaseManager
from app.utils.logger_enhanced import get_logger

bp = Blueprint('analytics', __name__)
logger = get_logger('analytics')

@bp.route('/analytics/operations', methods=['GET'])
def get_operation_analytics():
    """Get analytics for all operations"""
    try:
        analytics = DatabaseManager.get_analytics()
        
        result = {
            'success': True,
            'analytics': []
        }
        
        for record in analytics:
            # Convert tuple to dict (depending on DB structure)
            if isinstance(record, tuple):
                result['analytics'].append({
                    'operation_type': record[1],
                    'success_count': record[2],
                    'failure_count': record[3],
                    'total_files_processed': record[4],
                    'total_data_processed_mb': record[5],
                    'updated_at': str(record[6])
                })
            else:
                result['analytics'].append(record)
        
        logger.info(f"Analytics retrieved: {len(analytics)} operations")
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analytics/operations/<operation_type>', methods=['GET'])
def get_operation_detail(operation_type):
    """Get detailed analytics for specific operation"""
    try:
        analytics = DatabaseManager.get_analytics()
        
        for record in analytics:
            if record[1] == operation_type:
                result = {
                    'success': True,
                    'operation': operation_type,
                    'success_count': record[2],
                    'failure_count': record[3],
                    'total_files': record[4],
                    'total_data_mb': record[5],
                    'success_rate': (record[2] / (record[2] + record[3]) * 100) if (record[2] + record[3]) > 0 else 0
                }
                logger.info(f"Operation detail retrieved: {operation_type}")
                return jsonify(result)
        
        return jsonify({'success': False, 'error': 'Operation not found'}), 404
    
    except Exception as e:
        logger.error(f"Error retrieving operation detail: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get high-level analytics summary"""
    try:
        analytics = DatabaseManager.get_analytics()
        
        total_success = sum(record[2] for record in analytics)
        total_failures = sum(record[3] for record in analytics)
        total_files = sum(record[4] for record in analytics)
        total_data = sum(record[5] for record in analytics)
        
        summary = {
            'success': True,
            'total_operations': len(analytics),
            'total_successful': total_success,
            'total_failed': total_failures,
            'total_files_processed': total_files,
            'total_data_processed_mb': round(total_data, 2),
            'average_success_rate': (total_success / (total_success + total_failures) * 100) if (total_success + total_failures) > 0 else 0
        }
        
        logger.info("Analytics summary retrieved")
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
