"""Multi-region deployment models for global distribution."""
from app.models import db
from datetime import datetime, timedelta
import json
from enum import Enum

class RegionStatus(str, Enum):
    """Region operational status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class RegionConfig(db.Model):
    """Configuration for deployed regions."""
    __tablename__ = 'region_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    region_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    region_name = db.Column(db.String(100), nullable=False)
    cloud_provider = db.Column(db.String(50), nullable=False)  # aws, gcp, azure, cloudflare
    primary_endpoint = db.Column(db.String(255), nullable=False)
    database_host = db.Column(db.String(255), nullable=False)
    database_port = db.Column(db.Integer, default=5432)
    cdn_endpoint = db.Column(db.String(255))
    status = db.Column(db.String(20), default=RegionStatus.HEALTHY.value)
    is_primary = db.Column(db.Boolean, default=False)
    is_secondary = db.Column(db.Boolean, default=False)
    geo_latitude = db.Column(db.Float)
    geo_longitude = db.Column(db.Float)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Configuration metadata
    config_data = db.Column(db.JSON, default=dict)  # Extra config params
    
    # Health tracking
    last_health_check = db.Column(db.DateTime)
    health_check_failures = db.Column(db.Integer, default=0)
    consecutive_failures = db.Column(db.Integer, default=0)
    
    # Capacity metrics
    max_connections = db.Column(db.Integer, default=500)
    current_connections = db.Column(db.Integer, default=0)
    cpu_usage_percent = db.Column(db.Float, default=0.0)
    memory_usage_percent = db.Column(db.Float, default=0.0)
    disk_usage_percent = db.Column(db.Float, default=0.0)
    
    # Replication lag
    replication_lag_seconds = db.Column(db.Float, default=0.0)
    last_replication_check = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replicas = db.relationship('RegionReplica', foreign_keys='RegionReplica.primary_region_id', backref='primary_region', lazy='dynamic')
    health_history = db.relationship('RegionHealthHistory', backref='region', lazy='dynamic', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_region_status', 'status'),
        db.Index('idx_region_primary', 'is_primary'),
        db.Index('idx_region_health_check', 'last_health_check'),
    )
    
    def __repr__(self):
        return f'<RegionConfig {self.region_code}: {self.status}>'
    
    def is_healthy(self):
        """Check if region is healthy."""
        return self.status == RegionStatus.HEALTHY.value
    
    def get_health_percentage(self):
        """Calculate health based on failed checks."""
        if self.health_check_failures == 0:
            return 100
        return max(0, 100 - (self.health_check_failures * 5))
    
    def get_capacity_percentage(self):
        """Calculate region usage capacity."""
        capacities = [
            (self.current_connections / self.max_connections * 100) if self.max_connections > 0 else 0,
            self.cpu_usage_percent,
            self.memory_usage_percent,
            self.disk_usage_percent
        ]
        return sum(capacities) / len(capacities)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'region_code': self.region_code,
            'region_name': self.region_name,
            'cloud_provider': self.cloud_provider,
            'primary_endpoint': self.primary_endpoint,
            'cdn_endpoint': self.cdn_endpoint,
            'status': self.status,
            'is_primary': self.is_primary,
            'is_secondary': self.is_secondary,
            'coordinates': {
                'latitude': self.geo_latitude,
                'longitude': self.geo_longitude
            },
            'health_percentage': self.get_health_percentage(),
            'capacity_percentage': self.get_capacity_percentage(),
            'replication_lag_seconds': self.replication_lag_seconds,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
        }

class RegionReplica(db.Model):
    """Database replica configuration across regions."""
    __tablename__ = 'region_replicas'
    
    id = db.Column(db.Integer, primary_key=True)
    primary_region_id = db.Column(db.Integer, db.ForeignKey('region_configs.id'), nullable=False)
    replica_region_id = db.Column(db.Integer, db.ForeignKey('region_configs.id'), nullable=False)
    replication_status = db.Column(db.String(20), default='syncing')  # syncing, synced, failed
    replication_type = db.Column(db.String(50), default='async')  # async, semi-sync, sync
    
    # Replication metrics
    lag_bytes = db.Column(db.BigInteger, default=0)
    lag_seconds = db.Column(db.Float, default=0.0)
    last_sync_time = db.Column(db.DateTime)
    sync_failures = db.Column(db.Integer, default=0)
    
    # Configuration
    sync_interval_seconds = db.Column(db.Integer, default=60)
    failover_priority = db.Column(db.Integer, default=100)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    replica_region = db.relationship('RegionConfig', foreign_keys=[replica_region_id], backref='incoming_replicas')
    
    __table_args__ = (
        db.Index('idx_replica_status', 'replication_status'),
        db.Index('idx_replica_priority', 'failover_priority'),
        db.UniqueConstraint('primary_region_id', 'replica_region_id', name='unique_region_pair'),
    )
    
    def __repr__(self):
        return f'<RegionReplica {self.primary_region_id} → {self.replica_region_id}: {self.replication_status}>'
    
    def is_synced(self):
        """Check if replica is fully synced."""
        return self.replication_status == 'synced' and self.lag_seconds < 1.0

class GeoLocation(db.Model):
    """IP address to region mapping for geo-routing."""
    __tablename__ = 'geo_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False, index=True)
    ip_range = db.Column(db.String(50))  # CIDR notation
    country_code = db.Column(db.String(2), nullable=False, index=True)
    country_name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    region_code = db.Column(db.String(10), nullable=False, index=True)
    
    # Accuracy and source
    accuracy_km = db.Column(db.Float, default=100)  # Geo accuracy in KM
    data_source = db.Column(db.String(50), default='maxmind')  # maxmind, ip2location, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_geo_country', 'country_code'),
        db.Index('idx_geo_region', 'region_code'),
        db.Index('idx_geo_ip_range', 'ip_range'),
    )
    
    def __repr__(self):
        return f'<GeoLocation {self.ip_address} → {self.region_code}>'

class GeoRoute(db.Model):
    """Geo-routing policies for directing traffic by region."""
    __tablename__ = 'geo_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False, index=True)
    primary_region = db.Column(db.String(10), nullable=False)
    secondary_regions = db.Column(db.JSON, default=list)  # List of fallback regions
    weight_primary = db.Column(db.Integer, default=100)  # Traffic split percentage
    is_active = db.Column(db.Boolean, default=True)
    
    # Traffic policies
    enable_cdn = db.Column(db.Boolean, default=True)
    cache_ttl_seconds = db.Column(db.Integer, default=3600)
    compression_enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_route_country', 'country_code'),
        db.Index('idx_route_active', 'is_active'),
    )
    
    def __repr__(self):
        return f'<GeoRoute {self.country_code} → {self.primary_region}>'

class RegionHealthHistory(db.Model):
    """Health check history for regions."""
    __tablename__ = 'region_health_history'
    
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region_configs.id'), nullable=False)
    health_status = db.Column(db.String(20), nullable=False)
    response_time_ms = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    check_type = db.Column(db.String(50), default='http')  # http, database, replication
    
    # Metrics snapshot
    cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)
    disk_percent = db.Column(db.Float)
    active_connections = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_health_region_time', 'region_id', 'created_at'),
        db.Index('idx_health_status', 'health_status'),
    )
    
    def __repr__(self):
        return f'<RegionHealthHistory {self.region_id}: {self.health_status}>'
    
    def is_healthy(self):
        """Check if health check was successful."""
        return self.health_status == 'healthy'

class MultiRegionConfig(db.Model):
    """Global multi-region configuration."""
    __tablename__ = 'multi_region_config'
    
    id = db.Column(db.Integer, primary_key=True, default=1)
    
    # Global settings
    multi_region_enabled = db.Column(db.Boolean, default=True)
    health_check_interval_seconds = db.Column(db.Integer, default=60)
    failover_threshold_failures = db.Column(db.Integer, default=3)
    failover_cool_down_seconds = db.Column(db.Integer, default=300)
    
    # Replication settings
    cross_region_replication_enabled = db.Column(db.Boolean, default=True)
    default_replication_type = db.Column(db.String(20), default='async')
    replication_worker_threads = db.Column(db.Integer, default=5)
    
    # CDN settings
    cdn_provider = db.Column(db.String(50), default='cloudflare')  # cloudflare, cloudfront, akamai
    cdn_enabled = db.Column(db.Boolean, default=True)
    cdn_cache_ttl_seconds = db.Column(db.Integer, default=3600)
    cdn_purge_on_update = db.Column(db.Boolean, default=True)
    
    # Geo-routing settings
    geo_routing_enabled = db.Column(db.Boolean, default=True)
    geo_routing_default_region = db.Column(db.String(10), default='us')
    use_geolocation = db.Column(db.Boolean, default=True)
    use_latency_routing = db.Column(db.Boolean, default=False)
    
    # Performance settings
    enable_read_replicas = db.Column(db.Boolean, default=True)
    enable_write_forwarding = db.Column(db.Boolean, default=True)
    connection_pool_per_region = db.Column(db.Integer, default=20)
    
    # Monitoring
    monitoring_enabled = db.Column(db.Boolean, default=True)
    alert_email = db.Column(db.String(255))
    slack_webhook = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return '<MultiRegionConfig: Multi-region deployment>'

class RegionFailover(db.Model):
    """Track failover events across regions."""
    __tablename__ = 'region_failovers'
    
    id = db.Column(db.Integer, primary_key=True)
    primary_region_id = db.Column(db.Integer, db.ForeignKey('region_configs.id'), nullable=False)
    secondary_region_id = db.Column(db.Integer, db.ForeignKey('region_configs.id'), nullable=False)
    failover_reason = db.Column(db.String(255))
    failover_status = db.Column(db.String(50), default='pending')  # pending, in-progress, completed, rolled-back
    
    # Timing
    initiated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    # Details
    data_loss_records = db.Column(db.Integer, default=0)
    affected_users = db.Column(db.Integer, default=0)
    rollback_performed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    primary_region = db.relationship('RegionConfig', foreign_keys=[primary_region_id], backref='failovers_from')
    secondary_region = db.relationship('RegionConfig', foreign_keys=[secondary_region_id], backref='failovers_to')
    
    __table_args__ = (
        db.Index('idx_failover_status', 'failover_status'),
        db.Index('idx_failover_time', 'initiated_at'),
    )
    
    def __repr__(self):
        return f'<RegionFailover {self.primary_region_id} → {self.secondary_region_id}: {self.failover_status}>'
    
    def is_completed(self):
        """Check if failover is complete."""
        return self.failover_status == 'completed'
