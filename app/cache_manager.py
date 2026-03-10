"""Redis caching layer for DocPro."""
from flask_caching import Cache
from functools import wraps
from datetime import timedelta
import json
import hashlib

# Initialize cache
cache = Cache()

def init_cache(app):
    """Initialize caching with Flask app."""
    cache.init_app(app)

def cache_key_prefix(prefix):
    """Generate cache key with prefix."""
    return f"docpro:{prefix}"

def cached_endpoint(timeout=300, key_prefix='endpoint'):
    """Decorator for caching API endpoint responses."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Build cache key from function name and args
            cache_key = f"{key_prefix}:{f.__name__}"
            
            # Check cache
            cached = cache.get(cache_key)
            if cached:
                return cached
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return decorated_function
    return decorator

def invalidate_cache(pattern):
    """Invalidate cache by pattern."""
    cache.delete_many(*cache.keys(f"{pattern}*"))

class UserCacheManager:
    """Manage user-related caching."""
    
    PREFIX = cache_key_prefix("user")
    
    @staticmethod
    def user_key(user_id):
        return f"{UserCacheManager.PREFIX}:{user_id}"
    
    @staticmethod
    def get_user(user_id):
        """Get cached user."""
        return cache.get(UserCacheManager.user_key(user_id))
    
    @staticmethod
    def set_user(user_id, user_data, timeout=3600):
        """Cache user data."""
        cache.set(UserCacheManager.user_key(user_id), user_data, timeout=timeout)
    
    @staticmethod
    def invalidate_user(user_id):
        """Invalidate user cache."""
        cache.delete(UserCacheManager.user_key(user_id))

class ConversionCacheManager:
    """Manage conversion-related caching."""
    
    PREFIX = cache_key_prefix("conversion")
    
    @staticmethod
    def conversion_key(conversion_id):
        return f"{ConversionCacheManager.PREFIX}:{conversion_id}"
    
    @staticmethod
    def stats_key():
        return f"{ConversionCacheManager.PREFIX}:stats"
    
    @staticmethod
    def get_conversion(conversion_id):
        """Get cached conversion."""
        return cache.get(ConversionCacheManager.conversion_key(conversion_id))
    
    @staticmethod
    def set_conversion(conversion_id, data, timeout=1800):
        """Cache conversion data."""
        cache.set(ConversionCacheManager.conversion_key(conversion_id), data, timeout=timeout)
    
    @staticmethod
    def get_stats():
        """Get cached conversion stats."""
        return cache.get(ConversionCacheManager.stats_key())
    
    @staticmethod
    def set_stats(data, timeout=300):
        """Cache conversion stats."""
        cache.set(ConversionCacheManager.stats_key(), data, timeout=timeout)
    
    @staticmethod
    def invalidate_conversion(conversion_id):
        """Invalidate conversion cache."""
        cache.delete(ConversionCacheManager.conversion_key(conversion_id))
        # Also invalidate stats
        cache.delete(ConversionCacheManager.stats_key())

class AnalyticsCacheManager:
    """Manage analytics caching."""
    
    PREFIX = cache_key_prefix("analytics")
    
    @staticmethod
    def platform_stats_key():
        return f"{AnalyticsCacheManager.PREFIX}:platform:stats"
    
    @staticmethod
    def user_stats_key(user_id):
        return f"{AnalyticsCacheManager.PREFIX}:user:{user_id}:stats"
    
    @staticmethod
    def get_platform_stats():
        """Get cached platform stats."""
        return cache.get(AnalyticsCacheManager.platform_stats_key())
    
    @staticmethod
    def set_platform_stats(data, timeout=600):
        """Cache platform stats."""
        cache.set(AnalyticsCacheManager.platform_stats_key(), data, timeout=timeout)
    
    @staticmethod
    def get_user_stats(user_id):
        """Get cached user stats."""
        return cache.get(AnalyticsCacheManager.user_stats_key(user_id))
    
    @staticmethod
    def set_user_stats(user_id, data, timeout=600):
        """Cache user stats."""
        cache.set(AnalyticsCacheManager.user_stats_key(user_id), data, timeout=timeout)
    
    @staticmethod
    def invalidate_platform_stats():
        """Invalidate platform stats cache."""
        cache.delete(AnalyticsCacheManager.platform_stats_key())
    
    @staticmethod
    def invalidate_user_stats(user_id):
        """Invalidate user stats cache."""
        cache.delete(AnalyticsCacheManager.user_stats_key(user_id))

class SessionCacheManager:
    """Manage session/auth caching."""
    
    PREFIX = cache_key_prefix("session")
    
    @staticmethod
    def session_key(session_id):
        return f"{SessionCacheManager.PREFIX}:{session_id}"
    
    @staticmethod
    def get_session(session_id):
        """Get cached session."""
        return cache.get(SessionCacheManager.session_key(session_id))
    
    @staticmethod
    def set_session(session_id, data, timeout=86400):
        """Cache session data (24 hours default)."""
        cache.set(SessionCacheManager.session_key(session_id), data, timeout=timeout)
    
    @staticmethod
    def invalidate_session(session_id):
        """Invalidate session."""
        cache.delete(SessionCacheManager.session_key(session_id))

def cache_warmer(app):
    """Pre-load critical caches on startup."""
    with app.app_context():
        try:
            # Load platform statistics
            from app.models import db, Conversion, User
            from sqlalchemy import func
            
            total_users = User.query.count()
            total_conversions = Conversion.query.count()
            
            stats = {
                'total_users': total_users,
                'total_conversions': total_conversions,
            }
            
            AnalyticsCacheManager.set_platform_stats(stats)
            
        except Exception as e:
            print(f"Cache warmer error: {str(e)}")
