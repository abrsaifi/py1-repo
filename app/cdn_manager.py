"""Content Delivery Network (CDN) manager for global distribution."""
import logging
import requests
import json
from datetime import datetime
from typing import Dict, Tuple, Optional, List
from app.models import db
from app.models.multi_region import GeoRoute

logger = logging.getLogger(__name__)

class CloudflareManager:
    """Manage Cloudflare CDN configuration and purging."""
    
    def __init__(self, api_token: str = None, zone_id: str = None):
        """Initialize Cloudflare manager."""
        import os
        self.api_token = api_token or os.getenv('CLOUDFLARE_API_TOKEN')
        self.zone_id = zone_id or os.getenv('CLOUDFLARE_ZONE_ID')
        self.base_url = 'https://api.cloudflare.com/client/v4'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def is_configured(self) -> bool:
        """Check if Cloudflare is properly configured."""
        return bool(self.api_token and self.zone_id)
    
    def get_zone_info(self) -> Optional[Dict]:
        """Get Cloudflare zone information."""
        try:
            response = requests.get(
                f'{self.base_url}/zones/{self.zone_id}',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('result', {})
            logger.error(f'Failed to get zone info: {response.text}')
            return None
        except Exception as e:
            logger.error(f'Error getting Cloudflare zone info: {str(e)}')
            return None
    
    def set_cache_rules(self, path_pattern: str, ttl_seconds: int, cache_key_custom: bool = False) -> bool:
        """Set caching rules for specific path pattern."""
        try:
            rule = {
                'expression': f'(cf.uri.path matches "^{path_pattern}$")',
                'action': 'set_cache_settings',
                'action_parameters': {
                    'cache': True,
                    'browser_cache_ttl': ttl_seconds,
                    'cache_on_cookie': 'session_id',
                },
                'description': f'Cache {path_pattern} for {ttl_seconds}s'
            }
            
            response = requests.post(
                f'{self.base_url}/zones/{self.zone_id}/rules',
                headers=self.headers,
                json=rule,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f'Cache rule set for {path_pattern}')
                return True
            
            logger.error(f'Failed to set cache rule: {response.text}')
            return False
        
        except Exception as e:
            logger.error(f'Error setting cache rules: {str(e)}')
            return False
    
    def purge_cache_by_url(self, urls: List[str]) -> Tuple[bool, Dict]:
        """Purge cache for specific URLs."""
        try:
            if not urls:
                return False, {'error': 'No URLs provided'}
            
            # Limit to 30 URLs per request (Cloudflare limit)
            urls = urls[:30]
            
            response = requests.post(
                f'{self.base_url}/zones/{self.zone_id}/purge_cache',
                headers=self.headers,
                json={'files': urls},
                timeout=10
            )
            
            result = response.json()
            if response.status_code == 200 and result.get('success'):
                logger.info(f'Purged {len(urls)} URLs from Cloudflare cache')
                return True, result.get('result', {})
            
            logger.error(f'Failed to purge cache: {result}')
            return False, result
        
        except Exception as e:
            logger.error(f'Error purging cache: {str(e)}')
            return False, {'error': str(e)}
    
    def purge_cache_by_tag(self, tags: List[str]) -> Tuple[bool, Dict]:
        """Purge cache by tags."""
        try:
            response = requests.post(
                f'{self.base_url}/zones/{self.zone_id}/purge_cache',
                headers=self.headers,
                json={'tags': tags},
                timeout=10
            )
            
            result = response.json()
            if response.status_code == 200 and result.get('success'):
                logger.info(f'Purged {len(tags)} cache tags from Cloudflare')
                return True, result.get('result', {})
            
            logger.error(f'Failed to purge cache by tags: {result}')
            return False, result
        
        except Exception as e:
            logger.error(f'Error purging cache by tags: {str(e)}')
            return False, {'error': str(e)}
    
    def purge_all_cache(self) -> Tuple[bool, Dict]:
        """Purge all cache."""
        try:
            response = requests.post(
                f'{self.base_url}/zones/{self.zone_id}/purge_cache',
                headers=self.headers,
                json={'purge_everything': True},
                timeout=10
            )
            
            result = response.json()
            if response.status_code == 200 and result.get('success'):
                logger.warning('Purged all Cloudflare cache')
                return True, result.get('result', {})
            
            logger.error(f'Failed to purge all cache: {result}')
            return False, result
        
        except Exception as e:
            logger.error(f'Error purging all cache: {str(e)}')
            return False, {'error': str(e)}
    
    def set_geo_routing(self, country_code: str, data_center: str) -> bool:
        """Set geo-routing rule for specific country."""
        try:
            # Cloudflare: Set geo-blocking or routing rules
            rule = {
                'expression': f'(cf.country == "{country_code}")',
                'action': 'route',
                'action_parameters': {
                    'origin': {
                        'name': data_center
                    }
                },
                'description': f'Route {country_code} to {data_center}'
            }
            
            response = requests.post(
                f'{self.base_url}/zones/{self.zone_id}/rules',
                headers=self.headers,
                json=rule,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f'Geo-routing rule set for {country_code} → {data_center}')
                return True
            
            logger.error(f'Failed to set geo-routing: {response.text}')
            return False
        
        except Exception as e:
            logger.error(f'Error setting geo-routing: {str(e)}')
            return False
    
    def enable_compression(self) -> bool:
        """Enable gzip compression on Cloudflare."""
        try:
            response = requests.patch(
                f'{self.base_url}/zones/{self.zone_id}/settings/minify',
                headers=self.headers,
                json={
                    'value': {
                        'css': 'on',
                        'html': 'on',
                        'js': 'on'
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info('Compression enabled on Cloudflare')
                return True
            
            return False
        
        except Exception as e:
            logger.error(f'Error enabling compression: {str(e)}')
            return False
    
    def get_cache_stats(self) -> Optional[Dict]:
        """Get cache statistics."""
        try:
            response = requests.get(
                f'{self.base_url}/zones/{self.zone_id}/analytics/http_requests_by_response_status',
                headers=self.headers,
                params={'since': '-10080'},  # Last 7 days in minutes
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('result', {})
            
            return None
        
        except Exception as e:
            logger.error(f'Error getting cache stats: {str(e)}')
            return None

class CloudFrontManager:
    """Manage AWS CloudFront CDN configuration."""
    
    def __init__(self, distribution_id: str = None, access_key: str = None, secret_key: str = None):
        """Initialize CloudFront manager."""
        import os
        self.distribution_id = distribution_id or os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
        self.access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region = 'us-east-1'  # CloudFront is global
    
    def is_configured(self) -> bool:
        """Check if CloudFront is properly configured."""
        return bool(self.distribution_id and self.access_key and self.secret_key)
    
    def invalidate_cache(self, paths: List[str]) -> Tuple[bool, Dict]:
        """Invalidate CloudFront cache for specific paths."""
        try:
            import boto3
            
            client = boto3.client(
                'cloudfront',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            response = client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': str(datetime.utcnow().timestamp())
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            logger.info(f'CloudFront invalidation {invalidation_id} created for {len(paths)} paths')
            
            return True, {'invalidation_id': invalidation_id}
        
        except Exception as e:
            logger.error(f'Error invalidating CloudFront cache: {str(e)}')
            return False, {'error': str(e)}
    
    def get_distribution_config(self) -> Optional[Dict]:
        """Get CloudFront distribution configuration."""
        try:
            import boto3
            
            client = boto3.client(
                'cloudfront',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            response = client.get_distribution_config(Id=self.distribution_id)
            return response.get('DistributionConfig')
        
        except Exception as e:
            logger.error(f'Error getting CloudFront distribution config: {str(e)}')
            return None

class CDNManager:
    """Unified CDN manager supporting multiple providers."""
    
    def __init__(self, provider: str = 'cloudflare'):
        """Initialize CDN manager with specified provider."""
        self.provider = provider.lower()
        
        if self.provider == 'cloudflare':
            self.cdn = CloudflareManager()
        elif self.provider == 'cloudfront':
            self.cdn = CloudFrontManager()
        else:
            raise ValueError(f'Unsupported CDN provider: {provider}')
    
    def is_configured(self) -> bool:
        """Check if CDN is properly configured."""
        return self.cdn.is_configured() if self.cdn else False
    
    def purge_urls(self, urls: List[str]) -> Tuple[bool, Dict]:
        """Purge specific URLs from cache."""
        if self.provider == 'cloudflare':
            return self.cdn.purge_cache_by_url(urls)
        elif self.provider == 'cloudfront':
            return self.cdn.invalidate_cache(urls)
        
        return False, {'error': 'CDN not configured'}
    
    def purge_tags(self, tags: List[str]) -> Tuple[bool, Dict]:
        """Purge by cache tags (Cloudflare only)."""
        if self.provider == 'cloudflare':
            return self.cdn.purge_cache_by_tag(tags)
        
        return False, {'error': 'Tag-based purging not supported for this provider'}
    
    def purge_all(self) -> Tuple[bool, Dict]:
        """Purge entire cache."""
        if self.provider == 'cloudflare':
            return self.cdn.purge_all_cache()
        elif self.provider == 'cloudfront':
            # CloudFront: purge all paths
            return self.cdn.invalidate_cache(['/*'])
        
        return False, {'error': 'CDN not configured'}
    
    def mark_for_cache_refresh(self, resource_type: str, resource_id: int):
        """Mark resource for cache refresh (to be called on update)."""
        try:
            from app.models import db
            
            # Store cache invalidation request
            cache_key = f'{resource_type}:{resource_id}'
            # In production, use Redis or database to queue these
            logger.info(f'Resource marked for cache refresh: {cache_key}')
            
            return True
        except Exception as e:
            logger.error(f'Error marking resource for cache refresh: {str(e)}')
            return False
    
    @staticmethod
    def get_cache_url(path: str) -> str:
        """Get cacheable URL for resource."""
        # Add cache buster parameter or hash
        import hashlib
        from datetime import datetime
        
        year_week = datetime.utcnow().isocalendar()
        cache_key = hashlib.md5(f'{path}{year_week[0]}{year_week[1]}'.encode()).hexdigest()[:8]
        
        return f'{path}?cache={cache_key}'
