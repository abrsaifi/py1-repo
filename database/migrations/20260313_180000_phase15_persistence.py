"""Tracked Phase 15 schema migration for analytics and collaboration persistence."""
from sqlalchemy import inspect, text


MIGRATION = {
    'name': '20260313_180000_phase15_persistence',
    'description': 'Add persisted Phase 15 analytics reports and collaboration tables',
    'status': 'tracked',
    'tables': [
        'analytics_reports',
        'collaboration_documents',
        'document_shares',
        'document_comments',
        'collaboration_teams',
        'team_memberships',
        'collaboration_notifications',
        'notification_preferences',
        'collaboration_activity_logs',
    ],
}


UP = [
    """
    CREATE TABLE IF NOT EXISTS analytics_reports (
        id VARCHAR(36) PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        report_type VARCHAR(64) NOT NULL DEFAULT 'analytics',
        config JSON,
        export_format VARCHAR(16) NOT NULL DEFAULT 'pdf',
        last_run_at DATETIME,
        created_at DATETIME NOT NULL,
        updated_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_analytics_reports_user_id ON analytics_reports (user_id)",
    """
    CREATE TABLE IF NOT EXISTS collaboration_documents (
        id VARCHAR(36) PRIMARY KEY,
        owner_user_id INTEGER NOT NULL,
        name VARCHAR(255) NOT NULL,
        mime_type VARCHAR(255) NOT NULL DEFAULT 'application/octet-stream',
        file_size INTEGER NOT NULL DEFAULT 0,
        metadata_json JSON,
        created_at DATETIME NOT NULL,
        updated_at DATETIME,
        FOREIGN KEY(owner_user_id) REFERENCES users(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_collaboration_documents_owner_user_id ON collaboration_documents (owner_user_id)",
    """
    CREATE TABLE IF NOT EXISTS document_shares (
        id VARCHAR(36) PRIMARY KEY,
        document_id VARCHAR(36) NOT NULL,
        shared_by_user_id INTEGER NOT NULL,
        recipient_user_id INTEGER,
        recipient_email VARCHAR(255),
        permission VARCHAR(32) NOT NULL DEFAULT 'view',
        expires_at DATETIME,
        created_at DATETIME NOT NULL,
        FOREIGN KEY(document_id) REFERENCES collaboration_documents(id),
        FOREIGN KEY(shared_by_user_id) REFERENCES users(id),
        FOREIGN KEY(recipient_user_id) REFERENCES users(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_document_shares_document_id ON document_shares (document_id)",
    "CREATE INDEX IF NOT EXISTS idx_document_shares_recipient_user_id ON document_shares (recipient_user_id)",
    """
    CREATE TABLE IF NOT EXISTS document_comments (
        id VARCHAR(36) PRIMARY KEY,
        document_id VARCHAR(36) NOT NULL,
        author_user_id INTEGER NOT NULL,
        parent_comment_id VARCHAR(36),
        content TEXT NOT NULL,
        reactions JSON,
        created_at DATETIME NOT NULL,
        updated_at DATETIME,
        FOREIGN KEY(document_id) REFERENCES collaboration_documents(id),
        FOREIGN KEY(author_user_id) REFERENCES users(id),
        FOREIGN KEY(parent_comment_id) REFERENCES document_comments(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_document_comments_document_id ON document_comments (document_id)",
    """
    CREATE TABLE IF NOT EXISTS collaboration_teams (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        created_by_user_id INTEGER NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME,
        FOREIGN KEY(created_by_user_id) REFERENCES users(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS team_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id VARCHAR(36) NOT NULL,
        user_id INTEGER NOT NULL,
        role VARCHAR(32) NOT NULL DEFAULT 'member',
        created_at DATETIME NOT NULL,
        FOREIGN KEY(team_id) REFERENCES collaboration_teams(id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        CONSTRAINT uq_team_membership_team_user UNIQUE (team_id, user_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_team_memberships_team_id ON team_memberships (team_id)",
    "CREATE INDEX IF NOT EXISTS idx_team_memberships_user_id ON team_memberships (user_id)",
    """
    CREATE TABLE IF NOT EXISTS collaboration_notifications (
        id VARCHAR(36) PRIMARY KEY,
        user_id INTEGER NOT NULL,
        notification_type VARCHAR(64) NOT NULL,
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        link VARCHAR(255),
        is_read BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL,
        read_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_collaboration_notifications_user_id ON collaboration_notifications (user_id)",
    """
    CREATE TABLE IF NOT EXISTS notification_preferences (
        user_id INTEGER PRIMARY KEY,
        email_notifications BOOLEAN NOT NULL DEFAULT 1,
        in_app_notifications BOOLEAN NOT NULL DEFAULT 1,
        document_shared BOOLEAN NOT NULL DEFAULT 1,
        comment_added BOOLEAN NOT NULL DEFAULT 1,
        team_invitation BOOLEAN NOT NULL DEFAULT 1,
        report_generated BOOLEAN NOT NULL DEFAULT 1,
        daily_digest BOOLEAN NOT NULL DEFAULT 0,
        updated_at DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS collaboration_activity_logs (
        id VARCHAR(36) PRIMARY KEY,
        user_id INTEGER NOT NULL,
        action VARCHAR(64) NOT NULL,
        resource_type VARCHAR(64) NOT NULL,
        resource_id VARCHAR(64) NOT NULL,
        details JSON,
        created_at DATETIME NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_collaboration_activity_logs_user_id ON collaboration_activity_logs (user_id)",
    "CREATE INDEX IF NOT EXISTS idx_collaboration_activity_logs_action ON collaboration_activity_logs (action)",
]


DOWN = [
    'DROP TABLE IF EXISTS collaboration_activity_logs',
    'DROP TABLE IF EXISTS notification_preferences',
    'DROP TABLE IF EXISTS collaboration_notifications',
    'DROP TABLE IF EXISTS team_memberships',
    'DROP TABLE IF EXISTS collaboration_teams',
    'DROP TABLE IF EXISTS document_comments',
    'DROP TABLE IF EXISTS document_shares',
    'DROP TABLE IF EXISTS collaboration_documents',
    'DROP TABLE IF EXISTS analytics_reports',
]


def apply(engine):
    """Apply the migration against the provided SQLAlchemy engine."""
    existing_tables = set(inspect(engine).get_table_names())
    with engine.begin() as connection:
        for statement in UP:
            connection.execute(text(statement))
    return {
        'name': MIGRATION['name'],
        'applied_tables': [table for table in MIGRATION['tables'] if table not in existing_tables],
    }


def rollback(engine):
    """Rollback the migration against the provided SQLAlchemy engine."""
    with engine.begin() as connection:
        for statement in DOWN:
            connection.execute(text(statement))
    return {'name': MIGRATION['name'], 'rolled_back': list(MIGRATION['tables'])}