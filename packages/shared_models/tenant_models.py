"""
Multi-Tenancy Data Models
SQLAlchemy ORM models for multi-tenant SaaS platform

Features:
- Tenant organization and hierarchy
- Resource quotas and usage tracking
- SSO/SAML configuration
- Custom pricing and billing
- Team and department management
- White-label customization
- Webhook and integration management
- Comprehensive audit logging
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()


# ============================================================================
# Enums
# ============================================================================

class TenantStatus(str, enum.Enum):
    """Tenant account status"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"
    TRIAL = "TRIAL"
    ARCHIVED = "ARCHIVED"


class TenantTier(str, enum.Enum):
    """Tenant subscription tier"""
    STARTER = "STARTER"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class TenantPlanBillingCycle(str, enum.Enum):
    """Billing cycle for tenant"""
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    USAGE_BASED = "USAGE_BASED"


class TenantUserRole(str, enum.Enum):
    """User role within tenant"""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    GUEST = "GUEST"
    READONLY = "READONLY"


class SSOProvider(str, enum.Enum):
    """SSO/SAML provider type"""
    OKTA = "OKTA"
    AZURE_AD = "AZURE_AD"
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    ONELOGIN = "ONELOGIN"
    CUSTOM_SAML = "CUSTOM_SAML"
    OIDC = "OIDC"


class WebhookEventType(str, enum.Enum):
    """Types of webhook events"""
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    SUBSCRIPTION_CHANGED = "SUBSCRIPTION_CHANGED"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    USAGE_EXCEEDED = "USAGE_EXCEEDED"
    RESOURCE_CREATED = "RESOURCE_CREATED"
    RESOURCE_DELETED = "RESOURCE_DELETED"


class WebhookStatus(str, enum.Enum):
    """Webhook delivery status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FAILED = "FAILED"


class IntegrationType(str, enum.Enum):
    """Third-party integration type"""
    SLACK = "SLACK"
    STRIPE = "STRIPE"
    ZAPIER = "ZAPIER"
    GITHUB = "GITHUB"
    JIRA = "JIRA"
    SALESFORCE = "SALESFORCE"
    HUBSPOT = "HUBSPOT"
    CUSTOM = "CUSTOM"


class QuotaUnit(str, enum.Enum):
    """Unit for resource quotas"""
    COUNT = "COUNT"
    GB = "GB"
    MB = "MB"
    REQUESTS_PER_HOUR = "REQUESTS_PER_HOUR"
    REQUESTS_PER_MONTH = "REQUESTS_PER_MONTH"
    CONCURRENT_USERS = "CONCURRENT_USERS"


# ============================================================================
# Core Tenant Models
# ============================================================================

class Tenant(Base):
    """
    Multi-tenant organization
    
    Represents a single customer/organization in the SaaS platform
    """
    __tablename__ = 'tenants'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    website = Column(String(255))
    description = Column(String(1000))
    
    # Status and tier
    status = Column(Enum(TenantStatus), default=TenantStatus.ACTIVE, nullable=False, index=True)
    tier = Column(Enum(TenantTier), default=TenantTier.STARTER, nullable=False, index=True)
    
    # Location and timezone
    country = Column(String(100))
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    
    # Relationships
    parent_tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=True)  # For sub-tenants
    
    # Ownership
    owner_user_id = Column(String(36), nullable=True, index=True)
    
    # Plan info
    plan_name = Column(String(100))
    plan_seats = Column(Integer, default=1)
    plan_storage_gb = Column(Float, default=10.0)
    max_users = Column(Integer, default=10)
    
    # Trial info
    trial_starts_at = Column(DateTime)
    trial_ends_at = Column(DateTime)
    is_trial = Column(Boolean, default=False)
    
    # Custom branding
    logo_url = Column(String(500))
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))
    
    # Features
    enabled_features = Column(JSON, default=[])  # ['ocr', 'video_conversion', 'api_access']
    feature_limits = Column(JSON, default={})  # {ocr_monthly: 1000, video_conversions: 50}
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_status_created', 'status', 'created_at'),
        Index('idx_tenant_tier_status', 'tier', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'email': self.email,
            'status': self.status.value,
            'tier': self.tier.value,
            'max_users': self.max_users,
            'plan_storage_gb': self.plan_storage_gb,
            'is_trial': self.is_trial,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TenantConfiguration(Base):
    """
    Tenant-specific configuration and settings
    """
    __tablename__ = 'tenant_configurations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Configuration settings
    key = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # 'features', 'security', 'notifications', etc.
    value = Column(String(5000))
    value_type = Column(String(20), default='string')  # string, integer, boolean, json
    
    # Customization
    display_name = Column(String(255))
    description = Column(String(1000))
    
    # Access control
    is_restricted = Column(Boolean, default=False)  # Requires admin to change
    is_secret = Column(Boolean, default=False)  # Don't log or display value
    
    # Change tracking
    changed_by = Column(String(36))  # User ID
    changed_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'key', name='uq_tenant_config_key'),
        Index('idx_tenant_category', 'tenant_id', 'category'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'key': self.key,
            'category': self.category,
            'value': self.value if not self.is_secret else '***',
            'display_name': self.display_name,
            'is_restricted': self.is_restricted,
        }


class TenantUser(Base):
    """
    User membership in tenants with role assignment
    """
    __tablename__ = 'tenant_users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Role and permissions
    role = Column(Enum(TenantUserRole), default=TenantUserRole.MEMBER, nullable=False)
    custom_permissions = Column(JSON, default=[])  # Custom permission list
    
    # User status within tenant
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Team/Department assignment
    team_id = Column(String(36), ForeignKey('tenant_teams.id'), nullable=True)
    department_id = Column(String(36), ForeignKey('tenant_departments.id'), nullable=True)
    
    # MFA requirement
    require_mfa = Column(Boolean, default=False)
    
    # Time tracking
    invited_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    
    # Deletion (soft delete)
    deleted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'user_id', name='uq_tenant_user'),
        Index('idx_tenant_user_active', 'tenant_id', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'role': self.role.value,
            'is_active': self.is_active,
            'team_id': self.team_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TenantTeam(Base):
    """
    Teams within a tenant for organizational structure
    """
    __tablename__ = 'tenant_teams'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    # Team lead
    lead_user_id = Column(String(36), nullable=True)
    
    # Team structure
    parent_team_id = Column(String(36), ForeignKey('tenant_teams.id'), nullable=True)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_team_tenant', 'tenant_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'lead_user_id': self.lead_user_id,
        }


class TenantDepartment(Base):
    """
    Departments within teams for further organization
    """
    __tablename__ = 'tenant_departments'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    team_id = Column(String(36), ForeignKey('tenant_teams.id'), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    # Budget tracking
    budget_monthly = Column(Float, default=0.0)
    budget_used = Column(Float, default=0.0)
    
    # Manager
    manager_user_id = Column(String(36), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_dept_team', 'tenant_id', 'team_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'team_id': self.team_id,
            'name': self.name,
            'budget_monthly': self.budget_monthly,
            'budget_used': self.budget_used,
        }


# ============================================================================
# Quota and Usage Models
# ============================================================================

class TenantUsageQuota(Base):
    """
    Resource quotas for tenant features
    """
    __tablename__ = 'tenant_usage_quotas'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Feature/resource name
    feature_name = Column(String(100), nullable=False)
    resource_type = Column(String(50))  # 'api_calls', 'storage', 'users', etc.
    
    # Quota definition
    quota_limit = Column(Float, nullable=False)
    quota_unit = Column(Enum(QuotaUnit), default=QuotaUnit.COUNT)
    
    # Reset period
    reset_period_days = Column(Integer, default=30)  # Monthly reset
    reset_at = Column(DateTime, nullable=False)
    
    # Current usage
    quota_used = Column(Float, default=0.0)
    quota_percentage = Column(Float, default=0.0)
    last_reset_at = Column(DateTime)
    
    # Threshold alerts
    alert_at_percentage = Column(Integer, default=80)  # Alert when 80% used
    soft_limit = Column(Float, nullable=True)  # Grace limit above quota
    
    # Override
    is_unlimited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('tenant_id', 'feature_name', name='uq_tenant_feature_quota'),
        Index('idx_quota_usage', 'tenant_id', 'quota_used'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'feature_name': self.feature_name,
            'quota_limit': self.quota_limit,
            'quota_used': self.quota_used,
            'quota_percentage': self.quota_percentage,
        }


class TenantUsageMetrics(Base):
    """
    Detailed usage tracking and metrics per tenant
    """
    __tablename__ = 'tenant_usage_metrics'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Time period
    metric_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Usage metrics
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    
    # Context
    source_service = Column(String(100))  # Which service generated metric
    user_id = Column(String(36), nullable=True)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_metrics_tenant_date', 'tenant_id', 'metric_date'),
        Index('idx_metrics_name', 'tenant_id', 'metric_name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_date': self.metric_date.isoformat() if self.metric_date else None,
        }


# ============================================================================
# Billing and Pricing Models
# ============================================================================

class TenantBillingConfig(Base):
    """
    Custom billing configuration per tenant
    """
    __tablename__ = 'tenant_billing_configs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, unique=True, index=True)
    
    # Billing cycle
    billing_cycle = Column(Enum(TenantPlanBillingCycle), default=TenantPlanBillingCycle.MONTHLY)
    
    # Pricing (custom for enterprise)
    base_price_monthly = Column(Float, default=0.0)
    overage_price_per_unit = Column(Float, default=0.0)
    currency = Column(String(3), default='USD')
    
    # Pricing tiers (JSON for flexibility)
    custom_pricing_tiers = Column(JSON, default=[])  # [{users: 1-10, price: 100}, {users: 11-50, price: 80}]
    
    # Discounts
    discount_percentage = Column(Float, default=0.0)
    discount_reason = Column(String(255))
    discount_expires_at = Column(DateTime, nullable=True)
    
    # Annual prepay
    annual_prepay = Column(Boolean, default=False)
    annual_prepay_discount = Column(Float, default=0.0)
    
    # Billing contact
    billing_email = Column(String(255))
    billing_name = Column(String(255))
    
    # Payment method
    payment_method = Column(String(50))  # 'stripe', 'check', 'wire', 'invoice'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'billing_cycle': self.billing_cycle.value,
            'base_price_monthly': self.base_price_monthly,
            'currency': self.currency,
            'discount_percentage': self.discount_percentage,
        }


# ============================================================================
# SSO and Authentication Models
# ============================================================================

class TenantSSO(Base):
    """
    SSO/SAML configuration for tenant
    """
    __tablename__ = 'tenant_sso'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, unique=True, index=True)
    
    # SSO provider
    provider = Column(Enum(SSOProvider), nullable=False)
    
    # Configuration
    is_enabled = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)  # Require SSO for all users
    
    # Provider-specific settings
    provider_url = Column(String(500))  # SAML IdP URL, Okta org URL, etc.
    client_id = Column(String(255))
    client_secret = Column(String(500))  # Encrypted in production
    
    # SAML specific
    certificate_x509 = Column(String(5000), nullable=True)  # SAML X.509 cert
    metadata_url = Column(String(500), nullable=True)
    
    # Attribute mapping
    attribute_mapping = Column(JSON, default={})  # {'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress', ...}
    
    # User provisioning
    auto_provision_users = Column(Boolean, default=True)
    default_role = Column(Enum(TenantUserRole), default=TenantUserRole.MEMBER)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'provider': self.provider.value,
            'is_enabled': self.is_enabled,
            'is_required': self.is_required,
        }


# ============================================================================
# Integration Models
# ============================================================================

class TenantIntegration(Base):
    """
    Third-party integrations configured by tenant
    """
    __tablename__ = 'tenant_integrations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Integration type
    integration_type = Column(Enum(IntegrationType), nullable=False)
    
    # Configuration
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    # Credentials (encrypted)
    api_key = Column(String(500))
    api_secret = Column(String(500))
    webhook_secret = Column(String(500))
    
    # Configuration
    config = Column(JSON, default={})  # Provider-specific config
    
    # Status
    is_enabled = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    total_syncs = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_integration_type', 'tenant_id', 'integration_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'integration_type': self.integration_type.value,
            'name': self.name,
            'is_enabled': self.is_enabled,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TenantWebhook(Base):
    """
    Webhook endpoints for tenant event notifications
    """
    __tablename__ = 'tenant_webhooks'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Webhook configuration
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    
    # Event subscription
    event_types = Column(JSON, default=[])  # ['USER_CREATED', 'PAYMENT_RECEIVED', ...]
    
    # Authentication
    secret_key = Column(String(256))  # For HMAC signing
    
    # Status
    status = Column(Enum(WebhookStatus), default=WebhookStatus.ACTIVE)
    
    # Delivery tracking
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_webhook_status', 'tenant_id', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'url': self.url,
            'status': self.status.value,
            'event_types': self.event_types,
            'is_active': self.is_active,
        }


class TenantAPIKey(Base):
    """
    API keys for tenant to access platform APIs
    """
    __tablename__ = 'tenant_api_keys'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Key info
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    # Key hash (actual key not stored)
    key_hash = Column(String(256), unique=True, nullable=False, index=True)
    
    # Permissions
    scopes = Column(JSON, default=[])  # ['read:users', 'write:documents', ...]
    permissions = Column(JSON, default=[])
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=100)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # IP whitelist
    allowed_ips = Column(JSON, default=[])
    
    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    total_requests = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by = Column(String(36), nullable=True)
    
    __table_args__ = (
        Index('idx_key_tenant', 'tenant_id', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'scopes': self.scopes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================================
# Customization Models
# ============================================================================

class TenantCustomization(Base):
    """
    White-label customization for tenant
    """
    __tablename__ = 'tenant_customizations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, unique=True, index=True)
    
    # Branding
    company_name = Column(String(255))
    company_logo_url = Column(String(500))
    company_favicon_url = Column(String(500))
    
    # Colors
    primary_color = Column(String(7))  # Hex color
    secondary_color = Column(String(7))
    accent_color = Column(String(7))
    
    # Typography
    font_family = Column(String(100))  # CSS font name
    heading_font = Column(String(100))
    
    # Custom domains
    custom_domain = Column(String(255), nullable=True)
    custom_domain_ssl_cert = Column(String(5000), nullable=True)
    
    # Custom pages
    login_page_html = Column(String(10000), nullable=True)
    help_page_url = Column(String(500), nullable=True)
    privacy_policy_url = Column(String(500), nullable=True)
    terms_url = Column(String(500), nullable=True)
    
    # Email customization
    email_from_name = Column(String(255))
    email_from_address = Column(String(255))
    smtp_host = Column(String(255), nullable=True)  # Custom SMTP
    smtp_port = Column(Integer, nullable=True)
    
    # Features to show/hide
    hidden_features = Column(JSON, default=[])
    custom_menus = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'company_name': self.company_name,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'custom_domain': self.custom_domain,
        }


# ============================================================================
# Audit and Compliance Models
# ============================================================================

class TenantAuditLog(Base):
    """
    Tenant-level audit logs for compliance
    """
    __tablename__ = 'tenant_audit_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Event information
    event_type = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)  # create, update, delete, access
    
    # Who did it
    user_id = Column(String(36), nullable=True)
    admin_id = Column(String(36), nullable=True)  # If action by admin
    
    # What was affected
    resource_type = Column(String(50), nullable=False)  # user, config, integration, etc.
    resource_id = Column(String(36), nullable=False)
    
    # Changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changes_summary = Column(String(1000), nullable=True)
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Status
    status = Column(String(20), default='success')  # success, failure, partial
    error_message = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_audit_event_type', 'tenant_id', 'event_type'),
        Index('idx_audit_resource', 'tenant_id', 'resource_type', 'resource_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'event_type': self.event_type,
            'action': self.action,
            'resource_type': self.resource_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class TenantInvitation(Base):
    """
    User invitations to tenant
    """
    __tablename__ = 'tenant_invitations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Invitation details
    email = Column(String(255), nullable=False)
    role = Column(Enum(TenantUserRole), default=TenantUserRole.MEMBER)
    
    # Invitation token
    token = Column(String(256), unique=True, nullable=False, index=True)
    token_expires_at = Column(DateTime, nullable=False)
    
    # Status
    is_accepted = Column(Boolean, default=False)
    accepted_by_user_id = Column(String(36), nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # Sent by
    invited_by = Column(String(36), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_invitation_tenant_email', 'tenant_id', 'email'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'role': self.role.value,
            'is_accepted': self.is_accepted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# Export all models and enums
__all__ = [
    # Models
    'Tenant',
    'TenantConfiguration',
    'TenantUser',
    'TenantTeam',
    'TenantDepartment',
    'TenantUsageQuota',
    'TenantUsageMetrics',
    'TenantBillingConfig',
    'TenantSSO',
    'TenantIntegration',
    'TenantWebhook',
    'TenantAPIKey',
    'TenantCustomization',
    'TenantAuditLog',
    'TenantInvitation',
    # Enums
    'TenantStatus',
    'TenantTier',
    'TenantPlanBillingCycle',
    'TenantUserRole',
    'SSOProvider',
    'WebhookEventType',
    'WebhookStatus',
    'IntegrationType',
    'QuotaUnit',
]
