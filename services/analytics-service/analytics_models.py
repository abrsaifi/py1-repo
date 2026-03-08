"""
Analytics Data Models
Comprehensive models for system-wide analytics, metrics, and reporting
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, Index, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class MetricType(str, Enum):
    """Types of metrics"""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    RATE = "rate"
    PERCENTAGE = "percentage"


class AggregationLevel(str, Enum):
    """Aggregation granularity"""
    MINUTELY = "minute"
    HOURLY = "hour"
    DAILY = "day"
    WEEKLY = "week"
    MONTHLY = "month"
    YEARLY = "year"


class DashboardType(str, Enum):
    """Dashboard types"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    CUSTOM = "custom"


class ReportFrequency(str, Enum):
    """Report generation frequency"""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(str, Enum):
    """Alert status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    MUTED = "muted"


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class SystemMetric(Base):
    """System-wide metrics aggregation"""
    __tablename__ = 'system_metric'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    service_name = Column(String(100), nullable=False)
    metric_name = Column(String(150), nullable=False)
    metric_type = Column(String(20), nullable=False)
    aggregation_level = Column(String(20), nullable=False)
    
    # Time dimensions
    timestamp = Column(DateTime, nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Values
    value = Column(Float, nullable=False)
    min_value = Column(Float)
    max_value = Column(Float)
    avg_value = Column(Float)
    count = Column(Integer, default=0)
    
    # Metadata
    tags = Column(JSON, default={})
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_system_metric_tenant_service_time', 'tenant_id', 'service_name', 'timestamp'),
        Index('idx_system_metric_metric_name', 'metric_name'),
        Index('idx_system_metric_aggregation', 'aggregation_level', 'period_start'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'service': self.service_name,
            'metric': self.metric_name,
            'type': self.metric_type,
            'aggregation': self.aggregation_level,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'period': {'start': self.period_start.isoformat(), 'end': self.period_end.isoformat()},
            'value': self.value,
            'min': self.min_value,
            'max': self.max_value,
            'avg': self.avg_value,
            'count': self.count,
            'tags': self.tags,
            'metadata': self.metadata,
        }


class ServiceMetric(Base):
    """Per-service detailed metrics"""
    __tablename__ = 'service_metric'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    service_name = Column(String(100), nullable=False)
    
    # Timing metrics (milliseconds)
    response_time_p50 = Column(Float)  # 50th percentile
    response_time_p95 = Column(Float)  # 95th percentile
    response_time_p99 = Column(Float)  # 99th percentile
    response_time_avg = Column(Float)
    
    # Request metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    
    # Throughput
    requests_per_second = Column(Float, default=0.0)
    throughput_mbps = Column(Float, default=0.0)
    
    # Resource metrics
    cpu_usage_percent = Column(Float, default=0.0)
    memory_usage_percent = Column(Float, default=0.0)
    disk_usage_percent = Column(Float, default=0.0)
    
    # Errors
    error_count_4xx = Column(Integer, default=0)
    error_count_5xx = Column(Integer, default=0)
    timeout_count = Column(Integer, default=0)
    
    # Availability
    uptime_percent = Column(Float, default=100.0)
    last_health_check = Column(DateTime)
    
    # Timestamps
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_service_metric_tenant_service', 'tenant_id', 'service_name'),
        Index('idx_service_metric_period', 'period_start', 'period_end'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service_name,
            'response_time': {
                'p50': self.response_time_p50,
                'p95': self.response_time_p95,
                'p99': self.response_time_p99,
                'avg': self.response_time_avg,
            },
            'requests': {
                'total': self.total_requests,
                'successful': self.successful_requests,
                'failed': self.failed_requests,
                'error_rate': self.error_rate,
            },
            'throughput': {
                'rps': self.requests_per_second,
                'mbps': self.throughput_mbps,
            },
            'resources': {
                'cpu_percent': self.cpu_usage_percent,
                'memory_percent': self.memory_usage_percent,
                'disk_percent': self.disk_usage_percent,
            },
            'errors': {
                '4xx': self.error_count_4xx,
                '5xx': self.error_count_5xx,
                'timeouts': self.timeout_count,
            },
            'uptime_percent': self.uptime_percent,
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat(),
            },
        }


class UserActivityMetric(Base):
    """User activity and engagement metrics"""
    __tablename__ = 'user_activity_metric'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    
    # User counts
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)  # Last 24h
    new_users = Column(Integer, default=0)  # Today
    churned_users = Column(Integer, default=0)  # Haven't logged in 30+ days
    
    # Session metrics
    total_sessions = Column(Integer, default=0)
    avg_session_duration = Column(Float)  # in seconds
    sessions_per_user = Column(Float)
    bounce_rate = Column(Float)  # percentage
    
    # Feature usage
    feature_usage = Column(JSON, default={})  # {'feature_name': count}
    most_used_features = Column(JSON, default={})  # top features
    
    # Engagement
    daily_active_users = Column(Integer, default=0)
    weekly_active_users = Column(Integer, default=0)
    monthly_active_users = Column(Integer, default=0)
    dau_wau_ratio = Column(Float)  # DAU/WAU engagement metric
    dau_mau_ratio = Column(Float)  # DAU/MAU stickiness metric
    
    # Device info
    top_devices = Column(JSON, default={})  # {'device_type': count}
    top_browsers = Column(JSON, default={})  # {'browser': count}
    top_os = Column(JSON, default={})  # {'os': count}
    
    # Geographic
    top_countries = Column(JSON, default={})
    top_cities = Column(JSON, default={})
    
    # Timestamps
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_activity_metric_tenant_period', 'tenant_id', 'period_start'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'users': {
                'total': self.total_users,
                'active': self.active_users,
                'new': self.new_users,
                'churned': self.churned_users,
            },
            'sessions': {
                'total': self.total_sessions,
                'avg_duration_sec': self.avg_session_duration,
                'per_user': self.sessions_per_user,
                'bounce_rate': self.bounce_rate,
            },
            'engagement': {
                'dau': self.daily_active_users,
                'wau': self.weekly_active_users,
                'mau': self.monthly_active_users,
                'dau_wau_ratio': self.dau_wau_ratio,
                'dau_mau_ratio': self.dau_mau_ratio,
            },
            'top_features': self.most_used_features,
            'top_devices': self.top_devices,
            'top_browsers': self.top_browsers,
            'top_os': self.top_os,
            'top_countries': self.top_countries,
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat(),
            },
        }


class BusinessMetric(Base):
    """Business KPIs and financial metrics"""
    __tablename__ = 'business_metric'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Float, default=0.0)
    recurring_revenue = Column(Float, default=0.0)  # MRR or ARR
    average_order_value = Column(Float)
    revenue_per_user = Column(Float)
    
    # Conversion metrics
    conversion_rate = Column(Float)  # percentage
    trial_to_paid_rate = Column(Float)
    churn_rate = Column(Float)
    retention_rate = Column(Float)
    
    # Customer metrics
    total_customers = Column(Integer, default=0)
    new_customers = Column(Integer, default=0)
    existing_customers = Column(Integer, default=0)
    churned_customers = Column(Integer, default=0)
    
    # Lifetime value
    customer_lifetime_value = Column(Float)
    customer_acquisition_cost = Column(Float)
    payback_period_months = Column(Float)
    
    # Growth metrics
    month_over_month_growth = Column(Float)  # percentage
    year_over_year_growth = Column(Float)  # percentage
    growth_rate = Column(Float)  # percentage
    
    # Expansion & contraction
    expansion_revenue = Column(Float, default=0.0)  # Upsells
    contraction_revenue = Column(Float, default=0.0)  # Downgrades
    net_revenue_retention = Column(Float)  # NRR percentage
    
    # Engagement quality
    product_adoption_rate = Column(Float)
    feature_adoption_rate = Column(Float)
    
    # Timestamps
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_business_metric_tenant_period', 'tenant_id', 'period_start'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'revenue': {
                'total': self.total_revenue,
                'recurring': self.recurring_revenue,
                'aov': self.average_order_value,
                'per_user': self.revenue_per_user,
            },
            'conversion': {
                'rate': self.conversion_rate,
                'trial_to_paid': self.trial_to_paid_rate,
                'churn_rate': self.churn_rate,
                'retention_rate': self.retention_rate,
            },
            'customers': {
                'total': self.total_customers,
                'new': self.new_customers,
                'existing': self.existing_customers,
                'churned': self.churned_customers,
            },
            'ltv_lac': {
                'ltv': self.customer_lifetime_value,
                'cac': self.customer_acquisition_cost,
                'payback_months': self.payback_period_months,
            },
            'growth': {
                'mom': self.month_over_month_growth,
                'yoy': self.year_over_year_growth,
                'current_rate': self.growth_rate,
            },
            'expansion': {
                'expansion_revenue': self.expansion_revenue,
                'contraction_revenue': self.contraction_revenue,
                'nrr': self.net_revenue_retention,
            },
            'adoption': {
                'product': self.product_adoption_rate,
                'features': self.feature_adoption_rate,
            },
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat(),
            },
        }


class Dashboard(Base):
    """Analytics dashboards with customizable widgets"""
    __tablename__ = 'dashboard'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    owner_user_id = Column(String(36), nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    dashboard_type = Column(String(50), nullable=False)  # executive, operational, technical, custom
    
    # Configuration
    layout = Column(JSON, default={})  # Grid layout configuration
    widgets = Column(JSON, default=[])  # Array of widget definitions
    time_range = Column(String(50), default='24h')  # 1h, 24h, 7d, 30d, custom
    auto_refresh_seconds = Column(Integer, default=300)
    is_public = Column(Boolean, default=False)
    
    # Sharing & permissions
    shared_with_users = Column(JSON, default=[])  # User IDs
    shared_with_groups = Column(JSON, default=[])  # Group IDs
    
    # Status
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_dashboard_tenant_owner', 'tenant_id', 'owner_user_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.dashboard_type,
            'layout': self.layout,
            'widgets': self.widgets,
            'time_range': self.time_range,
            'auto_refresh_seconds': self.auto_refresh_seconds,
            'is_public': self.is_public,
            'view_count': self.view_count,
            'last_viewed_at': self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Report(Base):
    """Analytics reports scheduled or on-demand"""
    __tablename__ = 'report'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    created_by_user_id = Column(String(36), nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)  # summary, detailed, custom
    
    # Content
    sections = Column(JSON, default=[])  # Array of report sections
    metrics_included = Column(JSON, default=[])  # Metric names
    charts_included = Column(JSON, default=[])  # Chart definitions
    
    # Schedule
    is_scheduled = Column(Boolean, default=False)
    frequency = Column(String(20))  # hourly, daily, weekly, monthly
    next_generation_at = Column(DateTime)
    recipients = Column(JSON, default=[])  # Email recipients
    
    # Status
    status = Column(String(20), default='pending')  # pending, generating, completed, failed
    generation_count = Column(Integer, default=0)
    last_generated_at = Column(DateTime)
    error_message = Column(Text)
    
    # Storage
    file_path = Column(String(255))  # S3 or local path
    file_format = Column(String(20), default='pdf')  # pdf, xlsx, html
    file_size_bytes = Column(Integer)
    
    # Metrics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_report_tenant_created_by', 'tenant_id', 'created_by_user_id'),
        Index('idx_report_status_scheduled', 'status', 'is_scheduled'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.report_type,
            'status': self.status,
            'scheduled': self.is_scheduled,
            'frequency': self.frequency,
            'next_generation': self.next_generation_at.isoformat() if self.next_generation_at else None,
            'last_generated': self.last_generated_at.isoformat() if self.last_generated_at else None,
            'generation_count': self.generation_count,
            'file_format': self.file_format,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat(),
        }


class Alert(Base):
    """Analytics-based alerts for anomalies and thresholds"""
    __tablename__ = 'alert'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Trigger condition
    metric_name = Column(String(150), nullable=False)
    condition_type = Column(String(50), nullable=False)  # threshold, anomaly, change
    threshold_value = Column(Float)
    comparison_operator = Column(String(10))  # >, <, >=, <=, ==, !=
    
    # For anomaly detection
    is_anomaly_detection = Column(Boolean, default=False)
    anomaly_sensitivity = Column(Float)  # 0.0-1.0
    
    # For change detection
    percent_change_threshold = Column(Float)  # percentage change
    
    # Execution
    evaluation_frequency = Column(String(20), default='1m')  # 1m, 5m, 15m, 1h
    
    # Notification
    severity = Column(String(20), default='warning')
    notification_channels = Column(JSON, default=[])  # email, slack, webhook, sms
    recipients = Column(JSON, default=[])
    
    # Status
    status = Column(String(20), default='active')
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    
    # History
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_alert_tenant_metric', 'tenant_id', 'metric_name'),
        Index('idx_alert_status_active', 'status', 'is_active'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'metric': self.metric_name,
            'condition': {
                'type': self.condition_type,
                'threshold': self.threshold_value,
                'operator': self.comparison_operator,
                'is_anomaly': self.is_anomaly_detection,
                'anomaly_sensitivity': self.anomaly_sensitivity,
                'percent_change': self.percent_change_threshold,
            },
            'evaluation_frequency': self.evaluation_frequency,
            'severity': self.severity,
            'channels': self.notification_channels,
            'status': self.status,
            'is_active': self.is_active,
            'last_triggered': self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            'trigger_count': self.trigger_count,
            'created_at': self.created_at.isoformat(),
        }


class AlertEvent(Base):
    """Alert trigger events with acknowledgments"""
    __tablename__ = 'alert_event'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    alert_id = Column(String(36), ForeignKey('alert.id'), nullable=False)
    
    # Trigger details
    metric_value = Column(Float, nullable=False)
    threshold_value = Column(Float)
    severity = Column(String(20), nullable=False)
    
    # Status & response
    status = Column(String(20), default='active')  # active, acknowledged, resolved, muted
    acknowledged_by = Column(String(36))
    acknowledged_at = Column(DateTime)
    acknowledgment_message = Column(Text)
    
    resolved_by = Column(String(36))
    resolved_at = Column(DateTime)
    resolution_message = Column(Text)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_count = Column(Integer, default=0)
    
    # Context
    metric_history = Column(JSON, default=[])  # Historical values
    metadata = Column(JSON, default={})
    
    triggered_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_alert_event_tenant_alert', 'tenant_id', 'alert_id'),
        Index('idx_alert_event_status_triggered', 'status', 'triggered_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'metric_value': self.metric_value,
            'threshold_value': self.threshold_value,
            'severity': self.severity,
            'status': self.status,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'triggered_at': self.triggered_at.isoformat(),
            'notification_sent': self.notification_sent,
        }


class CustomMetric(Base):
    """User-defined custom metrics"""
    __tablename__ = 'custom_metric'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    created_by_user_id = Column(String(36), nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Definition
    metric_formula = Column(Text, nullable=False)  # e.g., "requests_success / requests_total * 100"
    metric_unit = Column(String(50))  # %, ms, $, users, requests, etc.
    
    # Components
    component_metrics = Column(JSON, default=[])  # List of metrics used in formula
    
    # Calculation
    calculation_method = Column(String(50))  # simple, weighted, custom_script
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Storage
    calculation_count = Column(Integer, default=0)
    last_calculated_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_custom_metric_tenant_created', 'tenant_id', 'created_by_user_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'formula': self.metric_formula,
            'unit': self.metric_unit,
            'calculation_method': self.calculation_method,
            'components': self.component_metrics,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'calculation_count': self.calculation_count,
            'last_calculated': self.last_calculated_at.isoformat() if self.last_calculated_at else None,
        }


class AnalyticsQuery(Base):
    """Saved analytics queries and views"""
    __tablename__ = 'analytics_query'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, nullable=False)
    created_by_user_id = Column(String(36), nullable=False)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Query definition
    query_type = Column(String(50), nullable=False)  # sql, metric, advanced
    query_text = Column(Text, nullable=False)
    
    # Parameters
    parameters = Column(JSON, default={})
    filters = Column(JSON, default=[])
    
    # Result config
    time_range = Column(String(50), default='24h')
    groupby = Column(String(100))
    orderby = Column(String(100))
    limit = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_shared = Column(Boolean, default=False)
    shared_with = Column(JSON, default=[])
    
    # Metrics
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime)
    avg_execution_time_ms = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_analytics_query_tenant', 'tenant_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.query_type,
            'time_range': self.time_range,
            'groupby': self.groupby,
            'is_shared': self.is_shared,
            'execution_count': self.execution_count,
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'created_at': self.created_at.isoformat(),
        }
