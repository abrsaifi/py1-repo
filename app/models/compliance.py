"""
Audit Log and Compliance Models
Provides SQLAlchemy models for tracking compliance events, audit logs, and data access
"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, JSON, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime, timedelta, timezone
import uuid
from .base import Base
from app.utils.datetime_utils import utc_now_naive


class AuditLog(Base):
    """
    Immutable audit trail for all significant system events
    Used for SOC2 compliance logging, security auditing, and compliance investigations
    """
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Event classification
    event_type = Column(String(50), nullable=False, index=True)  # user.login, data.access, data.modify, etc.
    event_category = Column(String(50), nullable=False, index=True)  # authentication, authorization, data, system
    severity = Column(String(20), nullable=False, index=True)  # info, warning, critical
    
    # Actor information
    actor_type = Column(String(50), nullable=False)  # user, admin, system, api_key
    actor_id = Column(UUID(as_uuid=True), index=True)  # User ID or API key ID
    actor_name = Column(String(255))  # User email or API key name
    
    # Action details
    action = Column(String(100), nullable=False)  # create, read, update, delete, export
    resource_type = Column(String(50))  # user, file, conversion, subscription
    resource_id = Column(UUID(as_uuid=True), index=True)
    resource_name = Column(String(255))
    
    # Result
    result = Column(String(20), nullable=False)  # success, failure, partial
    status_code = Column(Integer)  # HTTP status code if applicable
    error_message = Column(Text)
    
    # Context
    ip_address = Column(String(50), index=True)
    user_agent = Column(Text)
    request_id = Column(String(100), index=True)  # Correlation ID for request trace
    endpoint = Column(String(255))  # API endpoint or operation
    
    # Data access specifics
    data_accessed = Column(JSONB)  # Fields accessed: {'user_id': '...', 'email': '...'}
    data_modified = Column(JSONB)  # Fields and values modified: {'status': {'old': '...', 'new': '...'}}
    data_deleted = Column(Boolean, default=False)  # Whether personal data was deleted
    
    # Compliance metadata
    gdpr_relevant = Column(Boolean, default=False, index=True)  # Contains personal data
    pii_involved = Column(Boolean, default=False)  # Personally Identifiable Information
    encryption_used = Column(Boolean, default=True)  # Data encrypted at rest
    
    # Retention policy
    retention_until = Column(DateTime, index=True)  # When this log expires
    retention_reason = Column(String(50))  # legal, regulatory, operational
    
    # Metadata
    timestamp = Column(DateTime, nullable=False, default=utc_now_naive, index=True)
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    
    # Indexing for efficient queries
    __table_args__ = (
        Index('idx_audit_timestamp_event', 'timestamp', 'event_type'),
        Index('idx_audit_actor_timestamp', 'actor_id', 'timestamp'),
        Index('idx_audit_resource_action', 'resource_type', 'resource_id', 'action'),
        Index('idx_audit_gdpr', 'gdpr_relevant', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.event_type} -> {self.result} at {self.timestamp}>"


class UserConsent(Base):
    """
    Track user consent for data processing, marketing, etc.
    Required for GDPR compliance
    """
    __tablename__ = 'user_consents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Consent types
    data_processing = Column(Boolean, default=False)  # General data processing
    marketing = Column(Boolean, default=False)  # Marketing communications
    analytics = Column(Boolean, default=False)  # Analytics tracking
    third_party_sharing = Column(Boolean, default=False)  # Share data with partners
    
    # Tracking
    consented_at = Column(DateTime, nullable=False, default=utc_now_naive)
    withdrawn_at = Column(DateTime)  # When consent was withdrawn
    consent_method = Column(String(50))  # web_form, email, api
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Documentation
    consent_version = Column(String(20))  # Version of privacy policy accepted
    consent_text = Column(Text)  # Full text of what was consented to
    
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    
    def is_active(self):
        """Check if consent is currently active (not withdrawn)"""
        return self.withdrawn_at is None


class DataAccessLog(Base):
    """
    Track who accessed what personal data and when
    Required for GDPR data subject access requests
    """
    __tablename__ = 'data_access_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Subject of access
    subject_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Who accessed it
    accessor_type = Column(String(50), nullable=False)  # admin, user, system
    accessor_id = Column(UUID(as_uuid=True), index=True)
    
    # What was accessed
    data_category = Column(String(100), nullable=False)  # personal_info, usage_data, conversion_history
    fields_accessed = Column(ARRAY(String), default=[])  # List of specific fields
    access_method = Column(String(50))  # api, web_ui, export, report
    access_reason = Column(String(255))  # User request, compliance, support
    
    # When and how
    timestamp = Column(DateTime, nullable=False, default=utc_now_naive, index=True)
    duration_seconds = Column(Integer)  # How long access was maintained
    
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    
    __table_args__ = (
        Index('idx_data_access_subject', 'subject_user_id', 'timestamp'),
    )


class DataDeletionRequest(Base):
    """
    Track GDPR right-to-be-forgotten deletion requests
    Immutable record of what was deleted and when
    """
    __tablename__ = 'data_deletion_requests'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Request details
    requested_at = Column(DateTime, nullable=False, default=utc_now_naive)
    requested_by = Column(String(50))  # user, admin, system
    request_reason = Column(String(255))  # GDPR article 17, data minimization, user request
    
    # Execution
    status = Column(String(50), nullable=False, default='pending')  # pending, approved, executing, completed, failed, cancelled
    approval_required = Column(Boolean, default=False)  # Needs admin approval
    approved_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True))  # Admin user ID
    
    # What was deleted
    data_categories = Column(ARRAY(String), default=[])  # personal_info, usage_data, files, etc.
    fields_deleted = Column(JSONB)  # Details of what was deleted
    total_records_deleted = Column(Integer, default=0)
    
    # Execution timeline
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Proof and evidence
    confirmation_sent = Column(Boolean, default=False)
    confirmation_sent_at = Column(DateTime)
    
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    
    __table_args__ = (
        Index('idx_deletion_user_status', 'user_id', 'status'),
        Index('idx_deletion_requested', 'requested_at'),
    )


class CompliancePolicy(Base):
    """
    Define organizational compliance policies and data retention rules
    """
    __tablename__ = 'compliance_policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Policy definition
    policy_type = Column(String(50), nullable=False)  # retention, encryption, access_control
    
    # Retention policy
    retention_days = Column(Integer)  # How many days to retain data before deletion
    data_category = Column(String(100), nullable=False)  # logs, user_data, conversions, etc.
    auto_delete = Column(Boolean, default=True)  # Automatically delete after retention period
    
    # Encryption policy
    encrypt_at_rest = Column(Boolean, default=True)
    encryption_algorithm = Column(String(50))  # AES-256, AES-128, etc.
    key_rotation_days = Column(Integer)  # Rotate keys every N days
    
    # Access control
    require_mfa_for_access = Column(Boolean, default=False)
    max_access_duration = Column(Integer)  # Maximum duration of access grant in hours
    audit_all_access = Column(Boolean, default=True)
    
    # Enabled status
    active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    updated_at = Column(DateTime, nullable=False, default=utc_now_naive, onupdate=utc_now_naive)
    created_by = Column(UUID(as_uuid=True))  # Admin who created policy


class SOC2Checkpoint(Base):
    """
    Track SOC2 compliance checkpoints and evidence collection
    """
    __tablename__ = 'soc2_checkpoints'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    checkpoint_name = Column(String(100), nullable=False)
    checkpoint_description = Column(Text)
    
    # Mapping to SOC2 criteria
    trust_service = Column(String(50))  # CC, A, C, I, P (Security, Availability, etc.)
    control_number = Column(String(20))  # CC6.1, A1.1, etc.
    
    # Evidence tracking
    status = Column(String(20), nullable=False, default='pending')  # pending, in-progress, passed, failed
    evidence_collected = Column(Boolean, default=False)
    evidence_location = Column(String(255))  # Where evidence is stored
    
    # Testing
    test_date = Column(DateTime)
    test_result = Column(String(50))  # pass, fail, conditional
    test_notes = Column(Text)
    
    # Audit trail
    last_verified_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True))
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=utc_now_naive)
    updated_at = Column(DateTime, nullable=False, default=utc_now_naive, onupdate=utc_now_naive)


# Helper functions for common audit operations

def create_audit_log(event_type, event_category, action, actor_id, actor_type='user',
                    resource_type=None, resource_id=None, result='success',
                    ip_address=None, status_code=None, error_message=None,
                    gdpr_relevant=False, pii_involved=False):
    """Helper to create audit log entry"""
    retention_days = 365 if gdpr_relevant else 90
    
    return AuditLog(
        event_type=event_type,
        event_category=event_category,
        action=action,
        actor_id=actor_id,
        actor_type=actor_type,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        ip_address=ip_address,
        status_code=status_code,
        error_message=error_message,
        gdpr_relevant=gdpr_relevant,
        pii_involved=pii_involved,
        retention_until=datetime.now(timezone.utc) + timedelta(days=retention_days),
        retention_reason='legal' if gdpr_relevant else 'regulatory',
        severity='critical' if not result == 'success' else 'info'
    )
