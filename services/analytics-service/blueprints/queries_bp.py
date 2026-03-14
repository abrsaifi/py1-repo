"""
Analytics Queries Blueprint
Endpoints for saved queries, query builder, and execution
"""

from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime, timezone
from functools import wraps
import uuid
import logging



queries_bp = Blueprint('queries', __name__, url_prefix='/queries')
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
# Query CRUD
# ============================================================================

@queries_bp.route('', methods=['GET'])
@require_tenant()
def list_queries():
    """
    GET /api/queries?limit=50&shared=false
    List saved queries
    """
    try:
        from analytics_models import AnalyticsQuery
        
        limit = min(int(request.args.get('limit', 50)), 500)
        shared_only = request.args.get('shared', 'false').lower() == 'true'
        
        session = current_app.SessionLocal()
        query = session.query(AnalyticsQuery).filter(
            AnalyticsQuery.tenant_id == g.tenant_id
        )
        
        if shared_only:
            query = query.filter(AnalyticsQuery.is_shared == True)
        
        queries = query.order_by(AnalyticsQuery.created_at.desc()).limit(limit).all()
        
        result = {
            'queries': [q.to_dict() for q in queries],
            'count': len(queries),
        }
        
        session.close()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing queries: {e}")
        return jsonify({'error': str(e)}), 500


@queries_bp.route('', methods=['POST'])
@require_tenant()
def create_query():
    """
    POST /api/queries
    Create new saved query
    
    Body: {
        "name": "Revenue by Country",
        "description": "Monthly revenue aggregated by country",
        "query_type": "metric",
        "query_text": "SELECT period_start, country, total_revenue FROM business_metrics",
        "parameters": {},
        "filters": [
            {"field": "period_start", "operator": ">=", "value": "2024-01-01"}
        ],
        "groupby": ["country"],
        "orderby": [{"field": "total_revenue", "direction": "desc"}],
        "limit": 100
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('name'):
            return jsonify({'error': 'Bad Request', 'message': 'name is required'}), 400
        
        session = current_app.SessionLocal()
        
        query = AnalyticsQuery(
            id=str(uuid.uuid4()),
            tenant_id=g.tenant_id,
            name=data.get('name'),
            description=data.get('description', ''),
            query_type=data.get('query_type', 'metric'),
            query_text=data.get('query_text', ''),
            parameters=data.get('parameters', {}),
            filters=data.get('filters', []),
            groupby=data.get('groupby', []),
            orderby=data.get('orderby', []),
            limit=data.get('limit', 100),
            created_by_user_id=g.user_id,
        )
        
        session.add(query)
        session.commit()
        
        result = query.to_dict()
        session.close()
        
        return jsonify({'success': True, 'query': result}), 201
    
    except Exception as e:
        logger.error(f"Error creating query: {e}")
        return jsonify({'error': str(e)}), 500


@queries_bp.route('/<query_id>', methods=['GET'])
@require_tenant()
def get_query(query_id):
    """GET /api/queries/{query_id}"""
    try:
        from analytics_models import AnalyticsQuery
        
        session = current_app.SessionLocal()
        query = session.query(AnalyticsQuery).filter(
            AnalyticsQuery.id == query_id,
            AnalyticsQuery.tenant_id == g.tenant_id
        ).first()
        
        if not query:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Query not found'}), 404
        
        result = query.to_dict()
        session.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting query: {e}")
        return jsonify({'error': str(e)}), 500


@queries_bp.route('/<query_id>', methods=['PUT'])
@require_tenant()
def update_query(query_id):
    """PUT /api/queries/{query_id}"""
    try:
        from analytics_models import AnalyticsQuery
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        query = session.query(AnalyticsQuery).filter(
            AnalyticsQuery.id == query_id,
            AnalyticsQuery.tenant_id == g.tenant_id
        ).first()
        
        if not query:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Query not found'}), 404
        
        if 'name' in data:
            query.name = data['name']
        if 'description' in data:
            query.description = data['description']
        if 'query_text' in data:
            query.query_text = data['query_text']
        if 'filters' in data:
            query.filters = data['filters']
        if 'limit' in data:
            query.limit = data['limit']
        
        session.commit()
        
        result = query.to_dict()
        session.close()
        
        return jsonify({'success': True, 'query': result}), 200
    
    except Exception as e:
        logger.error(f"Error updating query: {e}")
        return jsonify({'error': str(e)}), 500


@queries_bp.route('/<query_id>', methods=['DELETE'])
@require_tenant()
def delete_query(query_id):
    """DELETE /api/queries/{query_id}"""
    try:
        from analytics_models import AnalyticsQuery
        
        session = current_app.SessionLocal()
        query = session.query(AnalyticsQuery).filter(
            AnalyticsQuery.id == query_id,
            AnalyticsQuery.tenant_id == g.tenant_id
        ).first()
        
        if not query:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Query not found'}), 404
        
        session.delete(query)
        session.commit()
        session.close()
        
        return jsonify({'success': True, 'message': 'Query deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting query: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Query Execution
# ============================================================================

@queries_bp.route('/<query_id>/execute', methods=['POST'])
@require_tenant()
def execute_query(query_id):
    """
    POST /api/queries/{query_id}/execute
    Execute saved query
    
    Body: {
        "parameters": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
    }
    """
    try:
        from analytics_models import AnalyticsQuery
        
        data = request.get_json() or {}
        params = data.get('parameters', {})
        
        session = current_app.SessionLocal()
        query = session.query(AnalyticsQuery).filter(
            AnalyticsQuery.id == query_id,
            AnalyticsQuery.tenant_id == g.tenant_id
        ).first()
        
        if not query:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Query not found'}), 404
        
        try:
            # In real implementation, would execute query against database
            # This is a mock response showing structure
            results = []
            execution_time_ms = 245
            
            # Update execution stats
            query.execution_count = (query.execution_count or 0) + 1
            query.last_executed_at = datetime.now(timezone.utc)
            if query.avg_execution_time_ms:
                query.avg_execution_time_ms = (
                    (query.avg_execution_time_ms * (query.execution_count - 1) + execution_time_ms) /
                    query.execution_count
                )
            else:
                query.avg_execution_time_ms = execution_time_ms
            
            session.commit()
            session.close()
            
            return jsonify({
                'query_id': query_id,
                'query_name': query.name,
                'results': results,
                'row_count': len(results),
                'execution_time_ms': execution_time_ms,
            }), 200
        
        except Exception as exec_error:
            session.close()
            return jsonify({
                'error': 'Bad Request',
                'message': f'Query execution failed: {str(exec_error)}'
            }), 400
    
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# Query Templates
# ============================================================================

@queries_bp.route('/templates', methods=['GET'])
@require_tenant()
def get_query_templates():
    """GET /api/queries/templates - Get query templates"""
    try:
        templates = {
            'revenue_by_country': {
                'name': 'Revenue by Country',
                'query': 'SELECT country, SUM(total_revenue) as revenue FROM business_metrics GROUP BY country',
                'parameters': {},
            },
            'monthly_growth': {
                'name': 'Monthly Growth Rate',
                'query': 'SELECT period_start, growth_rate FROM business_metrics ORDER BY period_start DESC',
                'parameters': {},
            },
            'service_performance': {
                'name': 'Service Performance',
                'query': 'SELECT service_name, AVG(response_time_p99) as p99_latency FROM service_metrics',
                'parameters': {},
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
# Query Sharing
# ============================================================================

@queries_bp.route('/<query_id>/share', methods=['POST'])
@require_tenant()
def share_query(query_id):
    """
    POST /api/queries/{query_id}/share
    Share query with users
    """
    try:
        from analytics_models import AnalyticsQuery
        
        data = request.get_json() or {}
        session = current_app.SessionLocal()
        
        query = session.query(AnalyticsQuery).filter(
            AnalyticsQuery.id == query_id,
            AnalyticsQuery.tenant_id == g.tenant_id
        ).first()
        
        if not query:
            session.close()
            return jsonify({'error': 'Not Found', 'message': 'Query not found'}), 404
        
        query.is_shared = data.get('is_shared', True)
        if 'shared_with' in data:
            query.shared_with = data['shared_with']
        
        session.commit()
        
        result = query.to_dict()
        session.close()
        
        return jsonify({'success': True, 'query': result}), 200
    
    except Exception as e:
        logger.error(f"Error sharing query: {e}")
        return jsonify({'error': str(e)}), 500
