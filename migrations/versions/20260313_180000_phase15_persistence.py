"""add persisted Phase 15 analytics and collaboration tables

Revision ID: 20260313_180000
Revises:
Create Date: 2026-03-13 18:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '20260313_180000'
down_revision = None
branch_labels = None
depends_on = None


def _has_table(table_name):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade():
    if not _has_table('analytics_reports'):
        op.create_table(
            'analytics_reports',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('report_type', sa.String(length=64), nullable=False, server_default='analytics'),
            sa.Column('config', sa.JSON(), nullable=True),
            sa.Column('export_format', sa.String(length=16), nullable=False, server_default='pdf'),
            sa.Column('last_run_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_analytics_reports_user_id', 'analytics_reports', ['user_id'])

    if not _has_table('collaboration_documents'):
        op.create_table(
            'collaboration_documents',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('owner_user_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('mime_type', sa.String(length=255), nullable=False, server_default='application/octet-stream'),
            sa.Column('file_size', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['owner_user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_collaboration_documents_owner_user_id', 'collaboration_documents', ['owner_user_id'])

    if not _has_table('document_shares'):
        op.create_table(
            'document_shares',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('document_id', sa.String(length=36), nullable=False),
            sa.Column('shared_by_user_id', sa.Integer(), nullable=False),
            sa.Column('recipient_user_id', sa.Integer(), nullable=True),
            sa.Column('recipient_email', sa.String(length=255), nullable=True),
            sa.Column('permission', sa.String(length=32), nullable=False, server_default='view'),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['document_id'], ['collaboration_documents.id']),
            sa.ForeignKeyConstraint(['recipient_user_id'], ['users.id']),
            sa.ForeignKeyConstraint(['shared_by_user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_document_shares_document_id', 'document_shares', ['document_id'])
        op.create_index('idx_document_shares_recipient_user_id', 'document_shares', ['recipient_user_id'])

    if not _has_table('document_comments'):
        op.create_table(
            'document_comments',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('document_id', sa.String(length=36), nullable=False),
            sa.Column('author_user_id', sa.Integer(), nullable=False),
            sa.Column('parent_comment_id', sa.String(length=36), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('reactions', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['author_user_id'], ['users.id']),
            sa.ForeignKeyConstraint(['document_id'], ['collaboration_documents.id']),
            sa.ForeignKeyConstraint(['parent_comment_id'], ['document_comments.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_document_comments_document_id', 'document_comments', ['document_id'])

    if not _has_table('collaboration_teams'):
        op.create_table(
            'collaboration_teams',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_by_user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    if not _has_table('team_memberships'):
        op.create_table(
            'team_memberships',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('team_id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(length=32), nullable=False, server_default='member'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['team_id'], ['collaboration_teams.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('team_id', 'user_id', name='uq_team_membership_team_user'),
        )
        op.create_index('idx_team_memberships_team_id', 'team_memberships', ['team_id'])
        op.create_index('idx_team_memberships_user_id', 'team_memberships', ['user_id'])

    if not _has_table('collaboration_notifications'):
        op.create_table(
            'collaboration_notifications',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('notification_type', sa.String(length=64), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('link', sa.String(length=255), nullable=True),
            sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('read_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_collaboration_notifications_user_id', 'collaboration_notifications', ['user_id'])

    if not _has_table('notification_preferences'):
        op.create_table(
            'notification_preferences',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('in_app_notifications', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('document_shared', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('comment_added', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('team_invitation', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('report_generated', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('daily_digest', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('user_id'),
        )

    if not _has_table('collaboration_activity_logs'):
        op.create_table(
            'collaboration_activity_logs',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('action', sa.String(length=64), nullable=False),
            sa.Column('resource_type', sa.String(length=64), nullable=False),
            sa.Column('resource_id', sa.String(length=64), nullable=False),
            sa.Column('details', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_collaboration_activity_logs_user_id', 'collaboration_activity_logs', ['user_id'])
        op.create_index('idx_collaboration_activity_logs_action', 'collaboration_activity_logs', ['action'])


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())
    if 'collaboration_activity_logs' in existing:
        op.drop_index('idx_collaboration_activity_logs_action', table_name='collaboration_activity_logs')
        op.drop_index('idx_collaboration_activity_logs_user_id', table_name='collaboration_activity_logs')
        op.drop_table('collaboration_activity_logs')
    if 'notification_preferences' in existing:
        op.drop_table('notification_preferences')
    if 'collaboration_notifications' in existing:
        op.drop_index('idx_collaboration_notifications_user_id', table_name='collaboration_notifications')
        op.drop_table('collaboration_notifications')
    if 'team_memberships' in existing:
        op.drop_index('idx_team_memberships_user_id', table_name='team_memberships')
        op.drop_index('idx_team_memberships_team_id', table_name='team_memberships')
        op.drop_table('team_memberships')
    if 'collaboration_teams' in existing:
        op.drop_table('collaboration_teams')
    if 'document_comments' in existing:
        op.drop_index('idx_document_comments_document_id', table_name='document_comments')
        op.drop_table('document_comments')
    if 'document_shares' in existing:
        op.drop_index('idx_document_shares_recipient_user_id', table_name='document_shares')
        op.drop_index('idx_document_shares_document_id', table_name='document_shares')
        op.drop_table('document_shares')
    if 'collaboration_documents' in existing:
        op.drop_index('idx_collaboration_documents_owner_user_id', table_name='collaboration_documents')
        op.drop_table('collaboration_documents')
    if 'analytics_reports' in existing:
        op.drop_index('idx_analytics_reports_user_id', table_name='analytics_reports')
        op.drop_table('analytics_reports')