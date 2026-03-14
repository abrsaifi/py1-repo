"""Safe schema bootstrap utilities for legacy SQLite deployments."""
from sqlalchemy import inspect, text

from app.models import APIKey, AnalyticsReport, BillingAuditLog, BillingInvoice, BillingProfile, CollaborationActivityLog, CollaborationDocument, CollaborationNotification, CollaborationTeam, ConnectedApp, Conversion, DocumentComment, DocumentShare, NotificationPreference, Page, SEOMetadata, Subscription, TeamMembership, User, UserSession, Widget, db


CORE_MODELS = [User, Subscription, BillingInvoice, BillingAuditLog, BillingProfile, APIKey, Conversion, UserSession, ConnectedApp]
FEATURE_MODELS = [
    Page,
    Widget,
    SEOMetadata,
    AnalyticsReport,
    CollaborationDocument,
    DocumentShare,
    DocumentComment,
    CollaborationTeam,
    TeamMembership,
    CollaborationNotification,
    NotificationPreference,
    CollaborationActivityLog,
]

LEGACY_USER_COLUMNS = {
    'first_name': 'VARCHAR(255)',
    'last_name': 'VARCHAR(255)',
    'plan': "VARCHAR(50) DEFAULT 'free'",
    'quota_gb': 'INTEGER DEFAULT 5',
    'used_gb': 'FLOAT DEFAULT 0.0',
    'is_verified': 'BOOLEAN DEFAULT 0',
    'two_factor_enabled': 'BOOLEAN DEFAULT 0',
    'analytics_opt_in': 'BOOLEAN DEFAULT 1',
    'marketing_opt_in': 'BOOLEAN DEFAULT 1',
    'personalization_opt_in': 'BOOLEAN DEFAULT 1',
    'deletion_requested_at': 'DATETIME',
    'updated_at': 'DATETIME',
    'last_login': 'DATETIME',
}

LEGACY_BILLING_INVOICE_COLUMNS = {
    'refunded_at': 'DATETIME',
    'refund_amount': 'FLOAT',
    'failure_code': 'VARCHAR(64)',
    'failure_reason': 'VARCHAR(255)',
    'gateway_reference_id': 'VARCHAR(128)',
    'processor_event_at': 'DATETIME',
    'status_note': 'VARCHAR(255)',
}


def _ensure_missing_tables(app, existing_tables, models):
    created_tables = []

    for model in models:
        table = model.__table__
        if table.name in existing_tables:
            continue

        table.create(bind=db.engine, checkfirst=True)
        existing_tables.add(table.name)
        created_tables.append(table.name)

    if created_tables:
        app.logger.info('Bootstrapped tables: %s', ', '.join(created_tables))

    return created_tables


def _ensure_legacy_user_columns(app):
    inspector = inspect(db.engine)
    if 'users' not in inspector.get_table_names():
        return []

    existing_columns = {column['name'] for column in inspector.get_columns('users')}
    added_columns = []

    with db.engine.begin() as connection:
        for column_name, column_sql in LEGACY_USER_COLUMNS.items():
            if column_name in existing_columns:
                continue

            connection.execute(text(f'ALTER TABLE users ADD COLUMN {column_name} {column_sql}'))
            added_columns.append(column_name)

        if 'plan' in added_columns:
            connection.execute(text("UPDATE users SET plan = 'free' WHERE plan IS NULL"))
        if 'quota_gb' in added_columns:
            connection.execute(text('UPDATE users SET quota_gb = 5 WHERE quota_gb IS NULL'))
        if 'used_gb' in added_columns:
            connection.execute(text('UPDATE users SET used_gb = 0.0 WHERE used_gb IS NULL'))
        if 'is_verified' in added_columns:
            connection.execute(text('UPDATE users SET is_verified = 0 WHERE is_verified IS NULL'))
        if 'two_factor_enabled' in added_columns:
            connection.execute(text('UPDATE users SET two_factor_enabled = 0 WHERE two_factor_enabled IS NULL'))
        if 'analytics_opt_in' in added_columns:
            connection.execute(text('UPDATE users SET analytics_opt_in = 1 WHERE analytics_opt_in IS NULL'))
        if 'marketing_opt_in' in added_columns:
            connection.execute(text('UPDATE users SET marketing_opt_in = 1 WHERE marketing_opt_in IS NULL'))
        if 'personalization_opt_in' in added_columns:
            connection.execute(text('UPDATE users SET personalization_opt_in = 1 WHERE personalization_opt_in IS NULL'))

    if added_columns:
        app.logger.info('Patched legacy users columns: %s', ', '.join(added_columns))

    return added_columns


def _ensure_legacy_billing_invoice_columns(app):
    inspector = inspect(db.engine)
    if 'billing_invoices' not in inspector.get_table_names():
        return []

    existing_columns = {column['name'] for column in inspector.get_columns('billing_invoices')}
    added_columns = []

    with db.engine.begin() as connection:
        for column_name, column_sql in LEGACY_BILLING_INVOICE_COLUMNS.items():
            if column_name in existing_columns:
                continue

            connection.execute(text(f'ALTER TABLE billing_invoices ADD COLUMN {column_name} {column_sql}'))
            added_columns.append(column_name)

    if added_columns:
        app.logger.info('Patched legacy billing_invoices columns: %s', ', '.join(added_columns))

    return added_columns


def ensure_feature_tables(app):
    """Repair legacy schema drift and create missing core/feature tables."""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())

        patched_columns = _ensure_legacy_user_columns(app)
        patched_invoice_columns = _ensure_legacy_billing_invoice_columns(app)
        if patched_columns or patched_invoice_columns:
            inspector = inspect(db.engine)
            existing_tables = set(inspector.get_table_names())

        created_core = _ensure_missing_tables(app, existing_tables, CORE_MODELS)
        created_features = _ensure_missing_tables(app, existing_tables, FEATURE_MODELS)

        if not patched_columns and not patched_invoice_columns and not created_core and not created_features:
            app.logger.info('Schema bootstrap skipped; required tables and columns already present')

        return {
            'patched_columns': patched_columns + patched_invoice_columns,
            'created_core_tables': created_core,
            'created_feature_tables': created_features,
        }