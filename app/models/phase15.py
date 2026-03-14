"""Phase 15 persisted models for analytics reporting and collaboration."""
from datetime import datetime
import uuid

from . import db
from app.utils.datetime_utils import utc_now_naive


def _uuid_str():
    return str(uuid.uuid4())


class AnalyticsReport(db.Model):
    """Saved analytics report definitions owned by users."""
    __tablename__ = 'analytics_reports'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    report_type = db.Column(db.String(64), nullable=False, default='analytics')
    config = db.Column(db.JSON, nullable=False, default=dict)
    export_format = db.Column(db.String(16), nullable=False, default='pdf')
    last_run_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type,
            'config': self.config or {},
            'export_format': self.export_format,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CollaborationDocument(db.Model):
    """Metadata for user-owned collaboration documents."""
    __tablename__ = 'collaboration_documents'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(255), nullable=False, default='application/octet-stream')
    file_size = db.Column(db.Integer, nullable=False, default=0)
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    shares = db.relationship('DocumentShare', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('DocumentComment', backref='document', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, shared_with=0):
        return {
            'id': self.id,
            'name': self.name,
            'owner_user_id': self.owner_user_id,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'metadata': self.metadata_json or {},
            'shared_with': shared_with,
            'created': self.created_at.isoformat() if self.created_at else None,
            'modified': self.updated_at.isoformat() if self.updated_at else None,
        }


class DocumentShare(db.Model):
    """Access grants for collaboration documents."""
    __tablename__ = 'document_shares'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    document_id = db.Column(db.String(36), db.ForeignKey('collaboration_documents.id'), nullable=False, index=True)
    shared_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    recipient_email = db.Column(db.String(255), index=True)
    permission = db.Column(db.String(32), nullable=False, default='view')
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'shared_by_user_id': self.shared_by_user_id,
            'recipient_user_id': self.recipient_user_id,
            'recipient_email': self.recipient_email,
            'permission': self.permission,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'shared_at': self.created_at.isoformat() if self.created_at else None,
        }


class DocumentComment(db.Model):
    """Threaded document comments."""
    __tablename__ = 'document_comments'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    document_id = db.Column(db.String(36), db.ForeignKey('collaboration_documents.id'), nullable=False, index=True)
    author_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    parent_comment_id = db.Column(db.String(36), db.ForeignKey('document_comments.id'), index=True)
    content = db.Column(db.Text, nullable=False)
    reactions = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    replies = db.relationship(
        'DocumentComment',
        cascade='all, delete-orphan',
        backref=db.backref('parent', remote_side=[id]),
        lazy='joined',
    )

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'author_user_id': self.author_user_id,
            'parent_comment_id': self.parent_comment_id,
            'content': self.content,
            'reactions': self.reactions or {},
            'created': self.created_at.isoformat() if self.created_at else None,
            'updated': self.updated_at.isoformat() if self.updated_at else None,
        }


class CollaborationTeam(db.Model):
    """User collaboration teams."""
    __tablename__ = 'collaboration_teams'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    members = db.relationship('TeamMembership', backref='team', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, members=0, role='member'):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'members': members,
            'created': self.created_at.isoformat() if self.created_at else None,
            'role': role,
        }


class TeamMembership(db.Model):
    """Memberships for collaboration teams."""
    __tablename__ = 'team_memberships'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(36), db.ForeignKey('collaboration_teams.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.String(32), nullable=False, default='member')
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('team_id', 'user_id', name='uq_team_membership_team_user'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined': self.created_at.isoformat() if self.created_at else None,
        }


class CollaborationNotification(db.Model):
    """Persisted in-app notifications."""
    __tablename__ = 'collaboration_notifications'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    notification_type = db.Column(db.String(64), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    read_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'link': self.link,
            'read': self.is_read,
            'created': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }


class NotificationPreference(db.Model):
    """User notification preferences."""
    __tablename__ = 'notification_preferences'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    in_app_notifications = db.Column(db.Boolean, default=True, nullable=False)
    document_shared = db.Column(db.Boolean, default=True, nullable=False)
    comment_added = db.Column(db.Boolean, default=True, nullable=False)
    team_invitation = db.Column(db.Boolean, default=True, nullable=False)
    report_generated = db.Column(db.Boolean, default=True, nullable=False)
    daily_digest = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    def to_dict(self):
        return {
            'email_notifications': self.email_notifications,
            'in_app_notifications': self.in_app_notifications,
            'document_shared': self.document_shared,
            'comment_added': self.comment_added,
            'team_invitation': self.team_invitation,
            'report_generated': self.report_generated,
            'daily_digest': self.daily_digest,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CollaborationActivityLog(db.Model):
    """Simple persisted collaboration activity/audit feed."""
    __tablename__ = 'collaboration_activity_logs'

    id = db.Column(db.String(36), primary_key=True, default=_uuid_str)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(64), nullable=False, index=True)
    resource_type = db.Column(db.String(64), nullable=False, index=True)
    resource_id = db.Column(db.String(64), nullable=False, index=True)
    details = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details or {},
            'timestamp': self.created_at.isoformat() if self.created_at else None,
        }