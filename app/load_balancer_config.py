"""Load Balancer Configuration and Session Affinity"""
from flask import request, session
from functools import wraps
import hashlib
import os

class LoadBalancerConfig:
    """Load balancer configuration and strategies"""
    
    # Load balancing methods
    ROUND_ROBIN = 'round_robin'
    LEAST_CONNECTIONS = 'least_connections'
    IP_HASH = 'ip_hash'
    WEIGHTED = 'weighted'
    STICKY_SESSIONS = 'sticky_sessions'
    
    # Failover strategies
    FAILOVER_ACTIVE_PASSIVE = 'active_passive'
    FAILOVER_ACTIVE_ACTIVE = 'active_active'
    FAILOVER_WEIGHTED = 'weighted'
    
    # Health check settings
    HEALTH_CHECK_INTERVAL = 10  # seconds
    HEALTH_CHECK_TIMEOUT = 5    # seconds
    HEALTH_CHECK_FAILURES = 3   # mark unhealthy after N failures
    HEALTH_CHECK_SUCCESSES = 2  # mark healthy after N successes

class SessionAffinity:
    """Session affinity (sticky sessions) implementation"""
    
    @staticmethod
    def get_server_hash(ip_address):
        """Generate consistent hash for IP address"""
        return hashlib.md5(ip_address.encode()).hexdigest()
    
    @staticmethod
    def get_session_id():
        """Get session ID for session affinity"""
        # Try to use session ID if available
        if 'session_id' in session:
            return session.get('session_id')
        
        # Fall back to request ID or generate new one
        from uuid import uuid4
        session_id = str(uuid4())
        session['session_id'] = session_id
        return session_id
    
    @staticmethod
    def set_server_cookie(response, server_id):
        """Set server ID in cookie for load balancer"""
        response.set_cookie(
            'srv_route',
            server_id,
            max_age=3600,
            path='/',
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response

class HealthCheckScheduler:
    """Schedule and manage health checks"""
    
    def __init__(self):
        self.check_tasks = []
        self.unhealthy_servers = set()
        self.check_history = {}
    
    def should_exclude_server(self, server):
        """Check if server should be excluded from load balancing"""
        return server in self.unhealthy_servers
    
    def mark_unhealthy(self, server):
        """Mark server as unhealthy"""
        if server not in self.check_history:
            self.check_history[server] = {'failures': 0, 'successes': 0}
        
        self.check_history[server]['failures'] += 1
        self.check_history[server]['successes'] = 0
        
        if self.check_history[server]['failures'] >= LoadBalancerConfig.HEALTH_CHECK_FAILURES:
            self.unhealthy_servers.add(server)
            print(f"Server {server} marked UNHEALTHY after {self.check_history[server]['failures']} failures")
    
    def mark_healthy(self, server):
        """Mark server as healthy"""
        if server not in self.check_history:
            self.check_history[server] = {'failures': 0, 'successes': 0}
        
        self.check_history[server]['successes'] += 1
        self.check_history[server]['failures'] = 0
        
        if self.check_history[server]['successes'] >= LoadBalancerConfig.HEALTH_CHECK_SUCCESSES:
            if server in self.unhealthy_servers:
                self.unhealthy_servers.discard(server)
                print(f"Server {server} marked HEALTHY after {self.check_history[server]['successes']} successes")

class CircuitBreaker:
    """Circuit breaker pattern for failing servers"""
    
    STATE_CLOSED = 'closed'      # Normal operation
    STATE_OPEN = 'open'          # Stop sending requests
    STATE_HALF_OPEN = 'half_open'  # Test recovery
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = self.STATE_CLOSED
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        if self.state == self.STATE_HALF_OPEN:
            self.state = self.STATE_CLOSED
    
    def record_failure(self):
        """Record failed request"""
        from datetime import datetime, timezone
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.failure_count >= self.failure_threshold:
            self.state = self.STATE_OPEN
    
    def can_attempt_request(self):
        """Check if request should be attempted"""
        from datetime import datetime, timedelta, timezone
        
        if self.state == self.STATE_CLOSED:
            return True
        
        if self.state == self.STATE_OPEN:
            # Try to recover after timeout
            if (datetime.now(timezone.utc) - self.last_failure_time > 
                timedelta(seconds=self.recovery_timeout)):
                self.state = self.STATE_HALF_OPEN
                self.failure_count = 0
                return True
            return False
        
        # HALF_OPEN state
        return True
    
    def get_state(self):
        """Get circuit breaker state"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
        }

class ConnectionPoolMonitor:
    """Monitor backend connection pools"""
    
    def __init__(self):
        self.pool_stats = {}
    
    def record_connection(self, server, duration_ms):
        """Record connection information"""
        if server not in self.pool_stats:
            self.pool_stats[server] = {
                'total_connections': 0,
                'avg_duration_ms': 0,
                'max_duration_ms': 0,
                'min_duration_ms': float('inf')
            }
        
        stats = self.pool_stats[server]
        stats['total_connections'] += 1
        
        # Update averages
        prev_avg = stats['avg_duration_ms']
        stats['avg_duration_ms'] = (prev_avg + duration_ms) / 2
        stats['max_duration_ms'] = max(stats['max_duration_ms'], duration_ms)
        stats['min_duration_ms'] = min(stats['min_duration_ms'], duration_ms)
    
    def get_stats(self, server=None):
        """Get connection pool statistics"""
        if server:
            return self.pool_stats.get(server, {})
        return self.pool_stats
    
    def should_rebalance(self):
        """Check if load should be rebalanced"""
        if not self.pool_stats:
            return False
        
        # Check if any server is significantly slower
        durations = [s['avg_duration_ms'] for s in self.pool_stats.values()]
        if not durations:
            return False
        
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        
        # Rebalance if max is > 2x average
        return max_duration > (avg_duration * 2)

def sticky_session_decorator(f):
    """Decorator to implement sticky sessions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get or create session ID
        session_id = SessionAffinity.get_session_id()
        
        # Store in request context for load balancer awareness
        request.session_id = session_id
        
        response = f(*args, **kwargs)
        
        # Set server affinity cookie if this is from a specific server
        if hasattr(request, 'server_id'):
            SessionAffinity.set_server_cookie(response, request.server_id)
        
        return response
    
    return decorated_function

# Global instances
health_scheduler = HealthCheckScheduler()
connection_monitor = ConnectionPoolMonitor()

def get_health_scheduler():
    """Get global health check scheduler"""
    return health_scheduler

def get_connection_monitor():
    """Get global connection monitor"""
    return connection_monitor
