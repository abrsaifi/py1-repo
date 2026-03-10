"""Multi-region deployment REST API endpoints."""
from flask import Blueprint, jsonify, request, current_app
from functools import wraps
from datetime import datetime, timedelta
from app.models import db
from app.models.multi_region import (
    RegionConfig, RegionReplica, GeoRoute, RegionHealthHistory,
    MultiRegionConfig, RegionFailover
)
from app.multi_region_manager import (
    GeoRouter, RegionHealthChecker, ReplicationManager, RegionFailoverManager
)
from app.cdn_manager import CDNManager
import logging

logger = logging.getLogger(__name__)

# Blueprint definition
bp = Blueprint('multi_region', __name__, url_prefix='/api/multi-region')

def admin_required(f):
    """Require admin authorization."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import verify_jwt_in_request, get_jwt
        
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if not claims.get('is_admin'):
                return {'error': 'Admin access required'}, 403
        except Exception as e:
            return {'error': 'Authorization required'}, 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# ================== Region Management ==================

@bp.route('/regions', methods=['GET'])
def list_regions():
    """Get list of all configured regions."""
    try:
        regions = RegionConfig.query.all()
        return jsonify({
            'status': 'success',
            'regions': [region.to_dict() for region in regions],
            'count': len(regions)
        }), 200
    except Exception as e:
        logger.error(f'Error listing regions: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/regions/<region_code>', methods=['GET'])
def get_region(region_code):
    """Get specific region details."""
    try:
        region = RegionConfig.query.filter_by(region_code=region_code).first()
        if not region:
            return {'error': 'Region not found'}, 404
        
        return jsonify({
            'status': 'success',
            'region': region.to_dict()
        }), 200
    except Exception as e:
        logger.error(f'Error getting region: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/regions', methods=['POST'])
@admin_required
def create_region():
    """Create a new region configuration."""
    try:
        data = request.get_json()
        
        region = RegionConfig(
            region_code=data['region_code'],
            region_name=data['region_name'],
            cloud_provider=data.get('cloud_provider', 'aws'),
            primary_endpoint=data['primary_endpoint'],
            database_host=data['database_host'],
            database_port=data.get('database_port', 5432),
            cdn_endpoint=data.get('cdn_endpoint'),
            is_primary=data.get('is_primary', False),
            geo_latitude=data.get('geo_latitude'),
            geo_longitude=data.get('geo_longitude'),
            timezone=data.get('timezone', 'UTC')
        )
        
        db.session.add(region)
        db.session.commit()
        
        logger.info(f'Region created: {region.region_code}')
        return jsonify({
            'status': 'success',
            'region': region.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating region: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/regions/<region_code>', methods=['PUT'])
@admin_required
def update_region(region_code):
    """Update region configuration."""
    try:
        region = RegionConfig.query.filter_by(region_code=region_code).first()
        if not region:
            return {'error': 'Region not found'}, 404
        
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(region, key) and key not in ['id', 'created_at']:
                setattr(region, key, value)
        
        region.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'Region updated: {region.region_code}')
        return jsonify({
            'status': 'success',
            'region': region.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating region: {str(e)}')
        return {'error': str(e)}, 500

# ================== Health Checks ==================

@bp.route('/health/check', methods=['POST'])
@admin_required
def check_region_health():
    """Trigger health check for specific region."""
    try:
        region_code = request.get_json().get('region_code')
        region = RegionConfig.query.filter_by(region_code=region_code).first()
        
        if not region:
            return {'error': 'Region not found'}, 404
        
        healthy, metrics = RegionHealthChecker.check_region_health(region)
        
        return jsonify({
            'status': 'success',
            'region': region.region_code,
            'healthy': healthy,
            'status': region.status,
            'metrics': metrics
        }), 200
    except Exception as e:
        logger.error(f'Error checking region health: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/health/check-all', methods=['POST'])
@admin_required
def check_all_regions_health():
    """Check health of all regions."""
    try:
        results = RegionHealthChecker.check_all_regions()
        
        healthy_count = sum(1 for r in results.values() if r['healthy'])
        total_count = len(results)
        
        return jsonify({
            'status': 'success',
            'healthy_regions': healthy_count,
            'total_regions': total_count,
            'results': results
        }), 200
    except Exception as e:
        logger.error(f'Error checking all regions health: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/health/history/<region_code>', methods=['GET'])
def get_region_health_history(region_code):
    """Get health check history for region."""
    try:
        region = RegionConfig.query.filter_by(region_code=region_code).first()
        if not region:
            return {'error': 'Region not found'}, 404
        
        limit = request.args.get('limit', 100, type=int)
        history = RegionHealthHistory.query.filter_by(region_id=region.id).order_by(
            RegionHealthHistory.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'region': region.region_code,
            'history': [
                {
                    'timestamp': h.created_at.isoformat(),
                    'health_status': h.health_status,
                    'response_time_ms': h.response_time_ms,
                    'check_type': h.check_type,
                    'error': h.error_message
                }
                for h in history
            ]
        }), 200
    except Exception as e:
        logger.error(f'Error getting health history: {str(e)}')
        return {'error': str(e)}, 500

# ================== Replication Management ==================

@bp.route('/replication/status', methods=['GET'])
def get_replication_status():
    """Get global replication status."""
    try:
        primary = RegionConfig.query.filter_by(is_primary=True).first()
        if not primary:
            return {'error': 'Primary region not found'}, 404
        
        status = ReplicationManager.get_replication_status(primary)
        
        return jsonify({
            'status': 'success',
            'replication': status
        }), 200
    except Exception as e:
        logger.error(f'Error getting replication status: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/replication/initialize', methods=['POST'])
@admin_required
def initialize_replication():
    """Initialize replication to a replica region."""
    try:
        data = request.get_json()
        primary_id = data.get('primary_region_id')
        replica_id = data.get('replica_region_id')
        replication_type = data.get('replication_type', 'async')
        
        success = ReplicationManager.initialize_replica(primary_id, replica_id, replication_type)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Replication initialized'}), 200
        else:
            return {'error': 'Failed to initialize replication'}, 500
    except Exception as e:
        logger.error(f'Error initializing replication: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/replication/sync', methods=['POST'])
@admin_required
def sync_replica():
    """Manually sync a specific replica."""
    try:
        data = request.get_json()
        replica_id = data.get('replica_id')
        
        replica = RegionReplica.query.get(replica_id)
        if not replica:
            return {'error': 'Replica not found'}, 404
        
        success, result = ReplicationManager.sync_replica(replica)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'result': result
        }), 200 if success else 500
    except Exception as e:
        logger.error(f'Error syncing replica: {str(e)}')
        return {'error': str(e)}, 500

# ================== Geo-Routing ==================

@bp.route('/geo-routing/detect', methods=['GET'])
def detect_client_region():
    """Detect client region based on IP."""
    try:
        client_ip = GeoRouter.get_client_ip()
        geo = GeoRouter.lookup_geolocation(client_ip)
        best_region = GeoRouter.get_best_region(client_ip)
        
        return jsonify({
            'status': 'success',
            'client_ip': client_ip,
            'geolocation': geo,
            'best_region': best_region.to_dict() if best_region else None
        }), 200
    except Exception as e:
        logger.error(f'Error detecting client region: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/geo-routing/routes', methods=['GET'])
def list_geo_routes():
    """Get all geo-routing rules."""
    try:
        routes = GeoRoute.query.filter_by(is_active=True).all()
        
        return jsonify({
            'status': 'success',
            'routes': [
                {
                    'country_code': r.country_code,
                    'primary_region': r.primary_region,
                    'secondary_regions': r.secondary_regions,
                    'weight_primary': r.weight_primary
                }
                for r in routes
            ]
        }), 200
    except Exception as e:
        logger.error(f'Error listing geo-routes: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/geo-routing/routes', methods=['POST'])
@admin_required
def create_geo_route():
    """Create new geo-routing rule."""
    try:
        data = request.get_json()
        
        route = GeoRoute(
            country_code=data['country_code'],
            primary_region=data['primary_region'],
            secondary_regions=data.get('secondary_regions', []),
            weight_primary=data.get('weight_primary', 100),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(route)
        db.session.commit()
        
        logger.info(f'Geo-route created for {route.country_code}')
        return jsonify({'status': 'success', 'route': route.country_code}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating geo-route: {str(e)}')
        return {'error': str(e)}, 500

# ================== Failover Management ==================

@bp.route('/failover/initiate', methods=['POST'])
@admin_required
def initiate_failover():
    """Initiate failover from primary to secondary region."""
    try:
        data = request.get_json()
        primary_id = data.get('primary_region_id')
        secondary_id = data.get('secondary_region_id')
        reason = data.get('reason', 'Manual failover')
        
        primary = RegionConfig.query.get(primary_id)
        secondary = RegionConfig.query.get(secondary_id)
        
        if not primary or not secondary:
            return {'error': 'Region not found'}, 404
        
        success = RegionFailoverManager.initiate_failover(primary, secondary, reason)
        
        if success:
            logger.warning(f'Failover initiated: {primary.region_code} → {secondary.region_code}')
            return jsonify({'status': 'success', 'message': 'Failover initiated'}), 200
        else:
            return {'error': 'Failed to initiate failover'}, 500
    except Exception as e:
        logger.error(f'Error initiating failover: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/failover/complete/<int:failover_id>', methods=['POST'])
@admin_required
def complete_failover(failover_id):
    """Mark failover as completed."""
    try:
        success = RegionFailoverManager.complete_failover(failover_id)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Failover completed'}), 200
        else:
            return {'error': 'Failover not found'}, 404
    except Exception as e:
        logger.error(f'Error completing failover: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/failover/rollback/<int:failover_id>', methods=['POST'])
@admin_required
def rollback_failover(failover_id):
    """Rollback a failover."""
    try:
        success = RegionFailoverManager.rollback_failover(failover_id)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Failover rolled back'}), 200
        else:
            return {'error': 'Failover not found'}, 404
    except Exception as e:
        logger.error(f'Error rolling back failover: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/failover/history', methods=['GET'])
def get_failover_history():
    """Get failover event history."""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = RegionFailoverManager.get_failover_history(limit)
        
        return jsonify({
            'status': 'success',
            'failovers': history
        }), 200
    except Exception as e:
        logger.error(f'Error getting failover history: {str(e)}')
        return {'error': str(e)}, 500

# ================== CDN Management ==================

@bp.route('/cdn/purge', methods=['POST'])
@admin_required
def purge_cdn_cache():
    """Purge CDN cache for specific URLs."""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        config = MultiRegionConfig.query.first()
        if not config or not config.cdn_enabled:
            return {'error': 'CDN not enabled'}, 400
        
        cdn = CDNManager(config.cdn_provider)
        success, result = cdn.purge_urls(urls)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'result': result
        }), 200 if success else 500
    except Exception as e:
        logger.error(f'Error purging CDN cache: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/cdn/purge-all', methods=['POST'])
@admin_required
def purge_all_cdn_cache():
    """Purge all CDN cache."""
    try:
        config = MultiRegionConfig.query.first()
        if not config or not config.cdn_enabled:
            return {'error': 'CDN not enabled'}, 400
        
        cdn = CDNManager(config.cdn_provider)
        success, result = cdn.purge_all()
        
        if success:
            logger.warning('All CDN cache purged')
            return jsonify({'status': 'success', 'result': result}), 200
        else:
            return {'error': result.get('error', 'Failed to purge cache')}, 500
    except Exception as e:
        logger.error(f'Error purging all CDN cache: {str(e)}')
        return {'error': str(e)}, 500

# ================== Configuration ==================

@bp.route('/config', methods=['GET'])
def get_multi_region_config():
    """Get global multi-region configuration."""
    try:
        config = MultiRegionConfig.query.first()
        if not config:
            return {'error': 'Configuration not initialized'}, 404
        
        return jsonify({
            'status': 'success',
            'config': {
                'multi_region_enabled': config.multi_region_enabled,
                'health_check_interval_seconds': config.health_check_interval_seconds,
                'cdn_provider': config.cdn_provider,
                'cdn_enabled': config.cdn_enabled,
                'geo_routing_enabled': config.geo_routing_enabled
            }
        }), 200
    except Exception as e:
        logger.error(f'Error getting config: {str(e)}')
        return {'error': str(e)}, 500

@bp.route('/config', methods=['PUT'])
@admin_required
def update_multi_region_config():
    """Update global multi-region configuration."""
    try:
        config = MultiRegionConfig.query.first()
        if not config:
            config = MultiRegionConfig()
            db.session.add(config)
        
        data = request.get_json()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info('Multi-region configuration updated')
        return jsonify({'status': 'success', 'message': 'Configuration updated'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating config: {str(e)}')
        return {'error': str(e)}, 500
