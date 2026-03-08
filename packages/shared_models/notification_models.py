"""
Notification Service Data Models
Comprehensive email, SMS, and push notification system with templating and tracking
"""

from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, Boolean, 
    ForeignKey, JSON, Float, Index, func, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import json

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCE = "bounce"
    UNSUBSCRIBE = "unsubscribe"
    SPAM = "spam"


class NotificationType(str, Enum):
    """Notification types for categorization"""
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"
    VERIFICATION = "verification"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    QUOTA_WARNING = "quota_warning"
    QUOTA_EXCEEDED = "quota_exceeded"
    BILLING_ALERT = "billing_alert"
    USER_INVITATION = "user_invitation"
    TEAM_INVITE = "team_invite"
    TWO_FACTOR = "two_factor"
    SECURITY_ALERT = "security_alert"
    API_ERROR = "api_error"
    DAILY_DIGEST = "daily_digest"
    ACTIVITY_REPORT = "activity_report"
    MAINTENANCE_ALERT = "maintenance_alert"
    FEATURE_ANNOUNCEMENT = "feature_announcement"
    CUSTOM = "custom"


class NotificationPriority(str, Enum):
    """Notification priority for queuing"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EmailProvider(str, Enum):
    """Email service providers"""
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"
    MAILGUN = "mailgun"
    SMTP = "smtp"
    SENDPULSE = "sendpulse"


class SMSProvider(str, Enum):
    """SMS service providers"""
    TWILIO = "twilio"
    AWS_SNS = "aws_sns"
    VONAGE = "vonage"
    PLIVO = "plivo"


class PushProvider(str, Enum):
    """Push notification providers"""
    FCM = "fcm"  # Firebase Cloud Messaging
    APNs = "apns"  # Apple Push Notification service
    ONESIGNAL = "onesignal"
    PUSHER = "pusher"


class PreferenceCategory(str, Enum):
    """Notification preference categories"""
    MARKETING = "marketing"
    TRANSACTIONAL = "transactional"
    SECURITY = "security"
    ACCOUNT = "account"
    BILLING = "billing"
    UPDATES = "updates"


class TemplateStatus(str, Enum):
    """Template status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UnsubscribeReason(str, Enum):
    """Reasons for unsubscribing"""
    NO_INTEREST = "no_interest"
    TOO_MANY = "too_many"
    NOT_RELEVANT = "not_relevant"
    SPAM = "spam"
    OTHER = "other"


# ============================================================================
# NOTIFICATION TEMPLATES
# ============================================================================

class NotificationTemplate(Base):
    """
    Email/SMS/Push notification templates with placeholders
    Supports multi-language and version control
    """
    __tablename__ = 'notification_templates'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Template identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    
    # Template content
    subject = Column(String(255))  # For email/SMS
    body = Column(Text, nullable=False)  # Main content
    preview_text = Column(String(255))  # Email preview
    footer = Column(Text)  # Optional footer
    
    # Template configuration
    placeholders = Column(JSON, default={})  # {placeholder: description}
    html_content = Column(Text)  # For HTML emails
    plain_text = Column(Text)  # Plain text fallback
    
    # Metadata
    language = Column(String(10), default='en')  # ISO 639-1
    version = Column(Integer, default=1)
    status = Column(SQLEnum(TemplateStatus), default=TemplateStatus.DRAFT)
    is_default = Column(Boolean, default=False)
    
    # Personalization
    supports_personalization = Column(Boolean, default=True)
    requires_action_url = Column(Boolean, default=False)
    
    # Performance
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    archived_at = Column(DateTime)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    __table_args__ = (
        Index('ix_tenant_channel_type', 'tenant_id', 'channel', 'notification_type'),
        Index('ix_tenant_status', 'tenant_id', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'description': self.description,
            'notification_type': self.notification_type.value,
            'channel': self.channel.value,
            'subject': self.subject,
            'body': self.body,
            'preview_text': self.preview_text,
            'footer': self.footer,
            'language': self.language,
            'version': self.version,
            'status': self.status.value,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


# ============================================================================
# EMAIL NOTIFICATIONS
# ============================================================================

class EmailNotification(Base):
    """
    Email notification records with delivery tracking
    Supports HTML, plain text, and attachments
    """
    __tablename__ = 'email_notifications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Recipient
    recipient_email = Column(String(255), nullable=False, index=True)
    recipient_name = Column(String(255))
    recipient_user_id = Column(String(36), index=True)
    
    # Email content
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    html_content = Column(Text)
    plain_text = Column(Text)
    
    # Template reference
    template_id = Column(String(36), ForeignKey('notification_templates.id'))
    template_name = Column(String(255))
    
    # Metadata
    notification_type = Column(SQLEnum(NotificationType), index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Delivery tracking
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Provider information
    email_provider = Column(SQLEnum(EmailProvider), default=EmailProvider.SENDGRID)
    provider_message_id = Column(String(255), index=True)
    provider_status = Column(String(50))
    
    # Failure tracking
    error_message = Column(Text)
    error_code = Column(String(50))
    bounce_type = Column(String(50))  # permanent, temporary, complaint
    failure_reason = Column(String(255))
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)
    
    # Attachments
    attachments = Column(JSON, default=[])  # [{name, url, mime_type, size}]
    
    # Personalization data
    personalization_data = Column(JSON, default={})
    
    # Tracking
    tracking_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    unsubscribe_token = Column(String(255), unique=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)  # Auto-delete old records
    
    __table_args__ = (
        Index('ix_tenant_status_created', 'tenant_id', 'status', 'created_at'),
        Index('ix_recipient_email_tenant', 'recipient_email', 'tenant_id'),
        Index('ix_provider_message_id', 'provider_message_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'recipient_email': self.recipient_email,
            'recipient_name': self.recipient_name,
            'subject': self.subject,
            'status': self.status.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat(),
        }


# ============================================================================
# SMS NOTIFICATIONS
# ============================================================================

class SMSNotification(Base):
    """
    SMS notification records with delivery tracking
    Supports single and bulk SMS sends
    """
    __tablename__ = 'sms_notifications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Recipient
    phone_number = Column(String(20), nullable=False, index=True)
    recipient_name = Column(String(255))
    recipient_user_id = Column(String(36), index=True)
    country_code = Column(String(3))
    
    # Content
    message_body = Column(String(1000), nullable=False)
    
    # Template reference
    template_id = Column(String(36), ForeignKey('notification_templates.id'))
    template_name = Column(String(255))
    
    # Metadata
    notification_type = Column(SQLEnum(NotificationType), index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Delivery tracking
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Provider information
    sms_provider = Column(SQLEnum(SMSProvider), default=SMSProvider.TWILIO)
    provider_message_id = Column(String(255), index=True)
    provider_status = Column(String(50))
    
    # Cost tracking
    cost = Column(Float)  # In USD
    currency = Column(String(3), default='USD')
    segments_count = Column(Integer, default=1)  # SMS segments
    
    # Failure tracking
    error_message = Column(Text)
    error_code = Column(String(50))
    failure_reason = Column(String(255))
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)
    
    # Personalization data
    personalization_data = Column(JSON, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)  # Auto-delete old records
    
    __table_args__ = (
        Index('ix_sms_tenant_status', 'tenant_id', 'status', 'created_at'),
        Index('ix_sms_phone_tenant', 'phone_number', 'tenant_id'),
        Index('ix_sms_provider_id', 'provider_message_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'phone_number': self.phone_number,
            'recipient_name': self.recipient_name,
            'status': self.status.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'cost': self.cost,
            'segments': self.segments_count,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
        }


# ============================================================================
# PUSH NOTIFICATIONS
# ============================================================================

class PushNotification(Base):
    """
    Push notification records for mobile apps
    Supports iOS (FCM), Android (APNs), and cross-platform
    """
    __tablename__ = 'push_notifications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Device targeting
    device_token = Column(String(500), nullable=False, index=True)
    device_id = Column(String(36), index=True)
    device_type = Column(String(50))  # ios, android, web
    app_version = Column(String(20))
    recipient_user_id = Column(String(36), index=True)
    
    # Notification content
    title = Column(String(255), nullable=False)
    body = Column(String(500), nullable=False)
    image_url = Column(String(500))
    icon_url = Column(String(500))
    
    # Actions
    action_type = Column(String(50))  # link, deep_link, action
    action_url = Column(String(500))
    action_data = Column(JSON, default={})
    
    # Template reference
    template_id = Column(String(36), ForeignKey('notification_templates.id'))
    template_name = Column(String(255))
    
    # Metadata
    notification_type = Column(SQLEnum(NotificationType), index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Delivery tracking
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Provider information
    push_provider = Column(SQLEnum(PushProvider), default=PushProvider.FCM)
    provider_message_id = Column(String(255), index=True)
    provider_status = Column(String(50))
    
    # Failure tracking
    error_message = Column(Text)
    error_code = Column(String(50))
    failure_reason = Column(String(255))
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)
    
    # Badge & sounds
    badge_count = Column(Integer)
    sound = Column(String(50))  # default, custom sound name
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)
    
    __table_args__ = (
        Index('ix_push_tenant_status', 'tenant_id', 'status', 'created_at'),
        Index('ix_push_device', 'device_token', 'tenant_id'),
        Index('ix_push_user', 'recipient_user_id', 'tenant_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'device_type': self.device_type,
            'title': self.title,
            'body': self.body,
            'status': self.status.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'created_at': self.created_at.isoformat(),
        }


# ============================================================================
# IN-APP NOTIFICATIONS
# ============================================================================

class InAppNotification(Base):
    """
    In-app notification records for dashboard/UI messages
    Supports different types: banner, modal, toast, badge
    """
    __tablename__ = 'in_app_notifications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    recipient_user_id = Column(String(36), nullable=False, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    icon_type = Column(String(50))  # info, success, warning, error
    
    # Display
    display_type = Column(String(50), default='banner')  # banner, modal, toast, badge
    position = Column(String(50), default='top')  # top, bottom, center
    duration_seconds = Column(Integer)  # For auto-dismiss
    
    # Actions
    action_label = Column(String(100))
    action_url = Column(String(500))
    action_type = Column(String(50))
    
    # Metadata
    notification_type = Column(SQLEnum(NotificationType), index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Status
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.SENT, index=True)
    read_at = Column(DateTime)
    dismissed_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    __table_args__ = (
        Index('ix_inapp_user_status', 'recipient_user_id', 'status', 'created_at'),
        Index('ix_inapp_tenant_user', 'tenant_id', 'recipient_user_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'message': self.message,
            'display_type': self.display_type,
            'icon_type': self.icon_type,
            'status': self.status.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
        }


# ============================================================================
# NOTIFICATION PREFERENCES & UNSUBSCRIBE
# ============================================================================

class NotificationPreference(Base):
    """
    User notification preferences by channel and type
    Respects opt-ins and opt-outs per category
    """
    __tablename__ = 'notification_preferences'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Preference scope
    channel = Column(SQLEnum(NotificationChannel), nullable=False, index=True)
    category = Column(SQLEnum(PreferenceCategory), nullable=False)
    
    # Permission
    is_enabled = Column(Boolean, default=True)
    
    # Frequency
    frequency = Column(String(50))  # immediate, hourly, daily, weekly, never
    
    # Unsubscribe
    is_unsubscribed = Column(Boolean, default=False)
    unsubscribe_reason = Column(SQLEnum(UnsubscribeReason))
    unsubscribe_at = Column(DateTime)
    resubscribe_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_pref_user_channel', 'user_id', 'channel', 'category'),
        Index('ix_pref_tenant_user', 'tenant_id', 'user_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'channel': self.channel.value,
            'category': self.category.value,
            'is_enabled': self.is_enabled,
            'frequency': self.frequency,
            'is_unsubscribed': self.is_unsubscribed,
            'unsubscribe_reason': self.unsubscribe_reason.value if self.unsubscribe_reason else None,
        }


class UnsubscribeLog(Base):
    """
    Track when users unsubscribe and their reasons
    Allows re-engagement campaigns
    """
    __tablename__ = 'unsubscribe_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Recipient
    email = Column(String(255), index=True)
    phone = Column(String(20), index=True)
    user_id = Column(String(36), index=True)
    
    # Unsubscribe reason
    channel = Column(SQLEnum(NotificationChannel))
    category = Column(SQLEnum(PreferenceCategory))
    reason = Column(SQLEnum(UnsubscribeReason))
    reason_details = Column(Text)
    
    # Token tracking
    unsubscribe_token = Column(String(255), unique=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('ix_unsub_tenant_email', 'tenant_id', 'email'),
        Index('ix_unsub_tenant_phone', 'tenant_id', 'phone'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'phone': self.phone,
            'channel': self.channel.value if self.channel else None,
            'category': self.category.value if self.category else None,
            'reason': self.reason.value if self.reason else None,
            'created_at': self.created_at.isoformat(),
        }


# ============================================================================
# NOTIFICATION QUEUE & BATCH OPERATIONS
# ============================================================================

class NotificationQueue(Base):
    """
    Queue for pending notifications before sending
    Supports batching, scheduling, and retry logic
    """
    __tablename__ = 'notification_queue'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Queue info
    notification_id = Column(String(36), nullable=False, index=True)
    notification_channel = Column(SQLEnum(NotificationChannel), nullable=False)
    notification_type = Column(SQLEnum(NotificationType))
    
    # Scheduling
    scheduled_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime)
    
    # Status
    is_processed = Column(Boolean, default=False, index=True)
    is_failed = Column(Boolean, default=False)
    error_message = Column(Text)
    
    # Priority
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_queue_tenant_status', 'tenant_id', 'is_processed', 'priority', 'scheduled_at'),
        Index('ix_queue_priority_scheduled', 'priority', 'scheduled_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'notification_id': self.notification_id,
            'notification_channel': self.notification_channel.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'priority': self.priority.value,
            'scheduled_at': self.scheduled_at.isoformat(),
            'is_processed': self.is_processed,
            'retry_count': self.retry_count,
        }


class NotificationBatch(Base):
    """
    Batch operations for sending bulk notifications
    Tracks batch progress and delivery metrics
    """
    __tablename__ = 'notification_batches'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Batch info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    batch_type = Column(SQLEnum(NotificationChannel), nullable=False)
    
    # Recipients
    total_recipients = Column(Integer, default=0)
    successful_sends = Column(Integer, default=0)
    failed_sends = Column(Integer, default=0)
    skipped_sends = Column(Integer, default=0)
    
    # Template
    template_id = Column(String(36), ForeignKey('notification_templates.id'))
    personalization_enabled = Column(Boolean, default=True)
    
    # Scheduling
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Status
    status = Column(String(50), default='pending')  # pending, in_progress, completed, failed
    progress_percentage = Column(Integer, default=0)
    
    # Results
    average_delivery_time = Column(Float)  # in seconds
    error_summary = Column(JSON, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('ix_batch_tenant_status', 'tenant_id', 'status', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'batch_type': self.batch_type.value,
            'total_recipients': self.total_recipients,
            'successful_sends': self.successful_sends,
            'failed_sends': self.failed_sends,
            'status': self.status,
            'progress': self.progress_percentage,
            'created_at': self.created_at.isoformat(),
        }


# ============================================================================
# NOTIFICATION ANALYTICS & LOGS
# ============================================================================

class NotificationLog(Base):
    """
    Comprehensive audit trail for all notification operations
    Tracks creation, sending, delivery, and user interactions
    """
    __tablename__ = 'notification_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    notification_id = Column(String(36), index=True)
    
    # Action details
    action = Column(String(50))  # created, sent, failed, delivered, opened, clicked, etc.
    action_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Channel and type
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    notification_type = Column(SQLEnum(NotificationType))
    
    # Status progression
    from_status = Column(String(50))
    to_status = Column(String(50))
    
    # Result
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Context
    user_id = Column(String(36), index=True)
    recipient_email = Column(String(255), index=True)
    recipient_phone = Column(String(20), index=True)
    
    # Metadata
    metadata = Column(JSON, default={})
    
    __table_args__ = (
        Index('ix_log_tenant_action', 'tenant_id', 'action', 'action_timestamp'),
        Index('ix_log_notification', 'notification_id', 'action_timestamp'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'action': self.action,
            'channel': self.channel.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'success': self.success,
            'action_timestamp': self.action_timestamp.isoformat(),
        }


class NotificationMetric(Base):
    """
    Aggregated notification metrics for analytics
    Hourly/daily summaries of delivery performance
    """
    __tablename__ = 'notification_metrics'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Time bucket
    metric_date = Column(DateTime, nullable=False, index=True)  # Start of hour/day
    period = Column(String(20))  # hourly, daily
    
    # Metrics
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    notification_type = Column(SQLEnum(NotificationType))
    
    # Counts
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    
    # Rates
    delivery_rate = Column(Float)  # 0-100
    open_rate = Column(Float)
    click_rate = Column(Float)
    
    # Costs
    cost = Column(Float, default=0)
    currency = Column(String(3), default='USD')
    
    # Created/updated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_metric_tenant_date', 'tenant_id', 'metric_date', 'channel'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'metric_date': self.metric_date.isoformat(),
            'channel': self.channel.value,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'total_sent': self.total_sent,
            'delivery_rate': self.delivery_rate,
            'open_rate': self.open_rate,
            'click_rate': self.click_rate,
            'cost': self.cost,
        }


# ============================================================================
# PROVIDER CONFIGURATION
# ============================================================================

class NotificationProviderConfig(Base):
    """
    Configuration for external notification providers
    Stores API keys, secrets, and provider-specific settings
    """
    __tablename__ = 'notification_provider_configs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Provider identification
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    provider_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Fallback if multiple
    
    # Credentials (encrypted in production)
    api_key = Column(String(500))
    api_secret = Column(String(500))
    account_id = Column(String(255))
    auth_token = Column(String(500))
    
    # Configuration
    sender_name = Column(String(255))  # For emails
    sender_email = Column(String(255))
    sender_phone = Column(String(20))
    from_number = Column(String(20))  # For SMS
    webhook_secret = Column(String(255))
    
    # Rate limiting
    rate_limit = Column(Integer)  # messages per second
    daily_limit = Column(Integer)
    
    # Features
    supports_batch_send = Column(Boolean, default=False)
    supports_scheduled_send = Column(Boolean, default=False)
    supports_tracking = Column(Boolean, default=True)
    supports_templates = Column(Boolean, default=False)
    
    # Statistics
    total_sent = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    average_delivery_time = Column(Float)  # in seconds
    
    # Health
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String(50))  # pending, verified, failed
    last_verified_at = Column(DateTime)
    last_error = Column(Text)
    last_error_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_config_tenant_channel', 'tenant_id', 'channel', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'channel': self.channel.value,
            'provider_name': self.provider_name,
            'is_active': self.is_active,
            'is_primary': self.is_primary,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'is_verified': self.is_verified,
            'total_sent': self.total_sent,
            'created_at': self.created_at.isoformat(),
        }
