"""Multi-region deployment manager for global distribution."""
import logging
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, Tuple, Optional, List
from flask import request
from app.models import db
from app.models.multi_region import (
    RegionConfig, RegionReplica, GeoLocation, GeoRoute, 
    RegionHealthHistory, MultiRegionConfig, RegionFailover, RegionStatus
)

logger = logging.getLogger(__name__)

class GeoRouter:
    """Route requests to appropriate region based on client geolocation."""
    
    @staticmethod
    def get_client_ip(req=None):
        """Extract client IP from request."""
        if req is None:
            req = request
        
        # Check X-Forwarded-For header (behind proxy)
        if req.headers.get('X-Forwarded-For'):
            return req.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        # Check X-Real-IP header
        if req.headers.get('X-Real-IP'):
            return req.headers.get('X-Real-IP')
        
        # Fall back to remote_addr
        return req.remote_addr
    
    @staticmethod
    def lookup_geolocation(ip_address: str) -> Optional[Dict]:
        """Lookup IP address to geolocation and region."""
        try:
            # Try database first for cached entries
            geo = GeoLocation.query.filter_by(ip_address=ip_address).first()
            if geo:
                return {
                    'country_code': geo.country_code,
                    'country_name': geo.country_name,
                    'city': geo.city,
                    'latitude': geo.latitude,
                    'longitude': geo.longitude,
                    'region_code': geo.region_code,
                }
            
            # Fall back to external geolocation service (e.g., ip-api.com)
            try:
                response = requests.get(
                    f'http://ip-api.com/json/{ip_address}',
                    timeout=2,
                    params={'fields': 'status,countryCode,city,lat,lon'}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'success':
                        return {
                            'country_code': data['countryCode'],
                            'city': data.get('city'),
                            'latitude': data.get('lat'),
                            'longitude': data.get('lon'),
                            'region_code': GeoRouter.map_country_to_region(data['countryCode']),
                        }
            except Exception as e:
                logger.warning(f'Geolocation service error for {ip_address}: {str(e)}')
            
            # Default to primary region
            return {'region_code': GeoRouter.get_default_region()}
        
        except Exception as e:
            logger.error(f'Error looking up geolocation for {ip_address}: {str(e)}')
            return {'region_code': GeoRouter.get_default_region()}
    
    @staticmethod
    def map_country_to_region(country_code: str) -> str:
        """Map ISO country code to region."""
        # US regions
        us_countries = {'US', 'MX', 'CA'}
        # EU regions
        eu_countries = {'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'CH', 'AT', 'SE', 'NO', 'DK', 'PL'}
        # APAC regions
        apac_countries = {'JP', 'SG', 'AU', 'NZ', 'IN', 'KR', 'CN', 'HK'}
        
        if country_code in us_countries:
            return 'us'
        elif country_code in eu_countries:
            return 'eu'
        elif country_code in apac_countries:
            return 'apac'
        else:
            return GeoRouter.get_default_region()
    
    @staticmethod
    def get_default_region() -> str:
        """Get default region from config."""
        config = MultiRegionConfig.query.first()
        if config:
            return config.geo_routing_default_region
        return 'us'  # Global default
    
    @staticmethod
    def get_best_region(client_ip: str = None) -> Optional[RegionConfig]:
        """Get best region for client based on geolocation."""
        if client_ip is None:
            client_ip = GeoRouter.get_client_ip()
        
        # Lookup geolocation
        geo = GeoRouter.lookup_geolocation(client_ip)
        region_code = geo.get('region_code') if geo else GeoRouter.get_default_region()
        
        # Get routing policy for this country/region
        route = GeoRoute.query.filter_by(
            country_code=geo.get('country_code') if geo else 'US',
            is_active=True
        ).first()
        
        if route and route.primary_region:
            region_code = route.primary_region
        
        # Get the region
        region = RegionConfig.query.filter_by(
            region_code=region_code,
            is_active=True if hasattr(RegionConfig, 'is_active') else None
        ).first()
        
        # If primary region unhealthy, use secondary
        if region and not region.is_healthy():
            if route and route.secondary_regions:
                for secondary_code in route.secondary_regions:
                    secondary = RegionConfig.query.filter_by(
                        region_code=secondary_code
                    ).first()
                    if secondary and secondary.is_healthy():
                        return secondary
        
        return region if region and region.is_healthy() else RegionConfig.query.filter_by(
            is_primary=True
        ).first()

class RegionHealthChecker:
    """Monitor health of regional endpoints."""
    
    HEALTH_CHECK_TIMEOUT = 5  # seconds
    
    @staticmethod
    def check_region_health(region: RegionConfig) -> Tuple[bool, Dict]:
        """Check if region is healthy via HTTP and database."""
        try:
            metrics = {
                'http_healthy': False,
                'database_healthy': False,
                'response_time_ms': 0,
                'error_message': None,
            }
            
            # HTTP health check
            try:
                response_time = RegionHealthChecker._check_http_health(region)
                metrics['http_healthy'] = response_time is not None
                metrics['response_time_ms'] = response_time or 0
            except Exception as e:
                metrics['error_message'] = f'HTTP check failed: {str(e)}'
                logger.warning(f'HTTP health check failed for region {region.region_code}: {str(e)}')
            
            # Database health check
            try:
                db_healthy = RegionHealthChecker._check_database_health(region)
                metrics['database_healthy'] = db_healthy
            except Exception as e:
                metrics['error_message'] = f'Database check failed: {str(e)}'
                logger.warning(f'Database health check failed for region {region.region_code}: {str(e)}')
            
            overall_healthy = metrics['http_healthy'] and metrics['database_healthy']
            
            # Log health history
            history = RegionHealthHistory(
                region_id=region.id,
                health_status='healthy' if overall_healthy else 'unhealthy',
                response_time_ms=metrics.get('response_time_ms', 0),
                error_message=metrics.get('error_message'),
                check_type='combined'
            )
            db.session.add(history)
            
            # Update region status
            if overall_healthy:
                region.status = RegionStatus.HEALTHY.value
                region.consecutive_failures = 0
                region.health_check_failures = max(0, region.health_check_failures - 1)
            else:
                region.consecutive_failures += 1
                region.health_check_failures += 1
                
                if region.consecutive_failures >= 3:
                    region.status = RegionStatus.UNHEALTHY.value
                elif region.consecutive_failures >= 1:
                    region.status = RegionStatus.DEGRADED.value
            
            region.last_health_check = datetime.utcnow()
            db.session.commit()
            
            return overall_healthy, metrics
        
        except Exception as e:
            logger.error(f'Error checking health for region {region.region_code}: {str(e)}')
            return False, {'error_message': str(e)}
    
    @staticmethod
    def _check_http_health(region: RegionConfig) -> Optional[int]:
        """Check HTTP health of region endpoint."""
        try:
            endpoint = f'{region.primary_endpoint}/health'
            response = requests.get(endpoint, timeout=RegionHealthChecker.HEALTH_CHECK_TIMEOUT)
            
            if response.status_code == 200:
                response_time = response.elapsed.total_seconds() * 1000  # Convert to ms
                return int(response_time)
            return None
        except Exception as e:
            logger.warning(f'HTTP health check failed for {region.region_code}: {str(e)}')
            return None
    
    @staticmethod
    def _check_database_health(region: RegionConfig) -> bool:
        """Check database connectivity for region."""
        try:
            # For now, implement simple connectivity check
            # In production, this would test actual DB connection
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((region.database_host, region.database_port))
            sock.close()
            
            return result == 0
        except Exception as e:
            logger.warning(f'Database health check failed for {region.region_code}: {str(e)}')
            return False
    
    @staticmethod
    def check_all_regions() -> Dict[str, bool]:
        """Check health of all configured regions."""
        results = {}
        regions = RegionConfig.query.all()
        
        for region in regions:
            healthy, metrics = RegionHealthChecker.check_region_health(region)
            results[region.region_code] = {
                'healthy': healthy,
                'status': region.status,
                'metrics': metrics
            }
        
        return results

class ReplicationManager:
    """Manage cross-region database replication."""
    
    @staticmethod
    def get_replication_status(primary_region: RegionConfig) -> Dict:
        """Get replication status from primary to all replicas."""
        status = {
            'primary_region': primary_region.region_code,
            'primary_healthy': primary_region.is_healthy(),
            'replicas': []
        }
        
        replicas = RegionReplica.query.filter_by(primary_region_id=primary_region.id).all()
        
        for replica in replicas:
            replica_status = {
                'replica_region': replica.replica_region.region_code,
                'replication_status': replica.replication_status,
                'lag_seconds': replica.lag_seconds,
                'synced': replica.is_synced(),
                'last_sync': replica.last_sync_time.isoformat() if replica.last_sync_time else None,
            }
            status['replicas'].append(replica_status)
        
        return status
    
    @staticmethod
    def sync_replica(replica: RegionReplica) -> Tuple[bool, Dict]:
        """Sync data from primary to replica region."""
        try:
            result = {
                'success': False,
                'duration_seconds': 0,
                'bytes_synced': 0,
                'error': None
            }
            
            start_time = datetime.utcnow()
            
            # Simulate replication (in production, use actual DB replication)
            # This would trigger WAL apply or snapshot transfer
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Update replica status
            replica.replication_status = 'synced'
            replica.last_sync_time = datetime.utcnow()
            replica.lag_seconds = 0.0
            replica.sync_failures = 0
            
            result['success'] = True
            result['duration_seconds'] = duration
            
            db.session.commit()
            logger.info(f'Replica sync completed for {replica.replica_region.region_code} in {duration}s')
            
            return True, result
        
        except Exception as e:
            replica.sync_failures += 1
            replica.replication_status = 'failed' if replica.sync_failures > 3 else 'syncing'
            db.session.commit()
            
            logger.error(f'Replica sync failed for {replica.replica_region.region_code}: {str(e)}')
            return False, {'error': str(e)}
    
    @staticmethod
    def initialize_replica(primary_id: int, replica_id: int, replication_type: str = 'async') -> bool:
        """Initialize replication from primary to replica region."""
        try:
            primary = RegionConfig.query.get(primary_id)
            replica = RegionConfig.query.get(replica_id)
            
            if not primary or not replica:
                logger.error('Primary or replica region not found')
                return False
            
            # Create replication config
            repl = RegionReplica.query.filter_by(
                primary_region_id=primary_id,
                replica_region_id=replica_id
            ).first()
            
            if not repl:
                repl = RegionReplica(
                    primary_region_id=primary_id,
                    replica_region_id=replica_id,
                    replication_type=replication_type,
                    replication_status='syncing'
                )
                db.session.add(repl)
            
            repl.replication_status = 'syncing'
            db.session.commit()
            
            logger.info(f'Replication initialized: {primary.region_code} → {replica.region_code}')
            return True
        
        except Exception as e:
            logger.error(f'Error initializing replication: {str(e)}')
            return False

class RegionFailoverManager:
    """Manage regional failover and recovery."""
    
    @staticmethod
    def initiate_failover(primary_region: RegionConfig, secondary_region: RegionConfig, reason: str) -> bool:
        """Initiate failover from primary to secondary region."""
        try:
            failover = RegionFailover(
                primary_region_id=primary_region.id,
                secondary_region_id=secondary_region.id,
                failover_reason=reason,
                failover_status='in-progress'
            )
            db.session.add(failover)
            
            # Update region statuses
            primary_region.status = RegionStatus.OFFLINE.value
            secondary_region.is_primary = True
            secondary_region.status = RegionStatus.HEALTHY.value
            
            db.session.commit()
            
            logger.warning(f'Failover initiated: {primary_region.region_code} → {secondary_region.region_code}. Reason: {reason}')
            
            return True
        
        except Exception as e:
            logger.error(f'Failover initiation failed: {str(e)}')
            return False
    
    @staticmethod
    def complete_failover(failover_id: int) -> bool:
        """Mark failover as completed."""
        try:
            failover = RegionFailover.query.get(failover_id)
            if not failover:
                return False
            
            failover.failover_status = 'completed'
            failover.completed_at = datetime.utcnow()
            failover.duration_seconds = int((failover.completed_at - failover.initiated_at).total_seconds())
            
            db.session.commit()
            logger.info(f'Failover completed in {failover.duration_seconds} seconds')
            
            return True
        
        except Exception as e:
            logger.error(f'Failover completion failed: {str(e)}')
            return False
    
    @staticmethod
    def rollback_failover(failover_id: int) -> bool:
        """Rollback a failover and restore primary region."""
        try:
            failover = RegionFailover.query.get(failover_id)
            if not failover:
                return False
            
            failover.rollback_performed = True
            failover.failover_status = 'rolled-back'
            
            primary = failover.primary_region
            secondary = failover.secondary_region
            
            # Restore original configuration
            primary.status = RegionStatus.HEALTHY.value
            primary.is_primary = True
            secondary.is_primary = False
            
            db.session.commit()
            logger.info(f'Failover rolled back: {secondary.region_code} → {primary.region_code}')
            
            return True
        
        except Exception as e:
            logger.error(f'Failover rollback failed: {str(e)}')
            return False
    
    @staticmethod
    def get_failover_history(limit: int = 20) -> List[Dict]:
        """Get recent failover events."""
        failovers = RegionFailover.query.order_by(
            RegionFailover.initiated_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': f.id,
                'primary': f.primary_region.region_code,
                'secondary': f.secondary_region.region_code,
                'reason': f.failover_reason,
                'status': f.failover_status,
                'duration_seconds': f.duration_seconds,
                'initiated_at': f.initiated_at.isoformat(),
                'completed_at': f.completed_at.isoformat() if f.completed_at else None,
            }
            for f in failovers
        ]
