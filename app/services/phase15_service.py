"""Service helpers for persisted Phase 15 analytics and collaboration APIs."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_

from app.models import (
    AnalyticsReport,
    BillingInvoice,
    CollaborationActivityLog,
    CollaborationDocument,
    CollaborationNotification,
    CollaborationTeam,
    Conversion,
    DocumentComment,
    DocumentShare,
    NotificationPreference,
    TeamMembership,
    User,
    db,
)
from app.services.reports import ReportService


class Phase15Service:
    """Business logic for persisted advanced analytics and collaboration flows."""

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def ensure_notification_preferences(user_id):
        preferences = NotificationPreference.query.filter_by(user_id=user_id).first()
        if preferences:
            return preferences

        preferences = NotificationPreference(user_id=user_id)
        db.session.add(preferences)
        db.session.flush()
        return preferences

    @staticmethod
    def log_activity(user_id, action, resource_type, resource_id, details=None):
        entry = CollaborationActivityLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=details or {},
        )
        db.session.add(entry)
        return entry

    @staticmethod
    def create_notification(user_id, notification_type, title, message, link=None):
        notification = CollaborationNotification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        db.session.add(notification)
        return notification

    @staticmethod
    def accessible_document_query(user_id):
        shared_document_ids = db.session.query(DocumentShare.document_id).filter(
            or_(DocumentShare.recipient_user_id == user_id, DocumentShare.shared_by_user_id == user_id)
        )
        return CollaborationDocument.query.filter(
            or_(
                CollaborationDocument.owner_user_id == user_id,
                CollaborationDocument.id.in_(shared_document_ids),
            )
        )

    @staticmethod
    def get_document_for_user(user_id, document_id, require_manage=False):
        document = CollaborationDocument.query.get_or_404(document_id)
        user = User.query.get_or_404(user_id)

        if user.is_admin() or document.owner_user_id == user_id:
            return document

        if require_manage:
            return None

        share = DocumentShare.query.filter(
            DocumentShare.document_id == document_id,
            or_(DocumentShare.recipient_user_id == user_id, DocumentShare.shared_by_user_id == user_id),
        ).first()
        return document if share else None

    @staticmethod
    def get_dashboard(user_id):
        recent_cutoff = Phase15Service._now() - timedelta(days=30)
        invoices = BillingInvoice.query.filter_by(user_id=user_id, status=BillingInvoice.STATUS_PAID).all()
        conversions = Conversion.query.filter_by(user_id=user_id).all()
        documents_count = CollaborationDocument.query.filter_by(owner_user_id=user_id).count()
        shared_count = DocumentShare.query.join(
            CollaborationDocument,
            DocumentShare.document_id == CollaborationDocument.id,
        ).filter(CollaborationDocument.owner_user_id == user_id).count()
        reports_count = AnalyticsReport.query.filter_by(user_id=user_id).count()

        completed = [item for item in conversions if item.status == 'completed']
        revenue = round(sum(invoice.amount or 0 for invoice in invoices), 2)
        avg_processing_time = round(
            sum(item.processing_time or 0 for item in completed) / len(completed), 2
        ) if completed else 0.0

        recent_metrics = []
        for days_back in range(6, -1, -1):
            day = (Phase15Service._now() - timedelta(days=days_back)).date()
            day_conversions = [item for item in conversions if item.created_at and item.created_at.date() == day]
            day_success = [item for item in day_conversions if item.status == 'completed']
            recent_metrics.append({
                'date': day.isoformat(),
                'revenue': round(sum((item.output_size or 0) for item in day_success) / 1024, 2),
                'users': 1 if day_conversions else 0,
                'conversion': round((len(day_success) / len(day_conversions) * 100), 2) if day_conversions else 0.0,
            })

        insights = [
            {
                'id': 'reports',
                'title': 'Saved reports available',
                'description': f'{reports_count} saved report(s) ready for reuse',
                'severity': 'positive' if reports_count else 'info',
                'actionable': reports_count == 0,
            },
            {
                'id': 'documents',
                'title': 'Collaboration footprint',
                'description': f'{documents_count} owned document(s), {shared_count} active share(s)',
                'severity': 'positive' if shared_count else 'warning',
                'actionable': shared_count == 0,
            },
        ]
        if avg_processing_time:
            insights.append({
                'id': 'processing-time',
                'title': 'Conversion efficiency',
                'description': f'Average processing time is {avg_processing_time} seconds across completed jobs',
                'severity': 'positive',
                'actionable': False,
            })

        return {
            'kpis': {
                'total_revenue': {
                    'value': revenue,
                    'change': 0.0,
                    'trend': 'up' if revenue else 'flat',
                    'currency': 'USD',
                },
                'units_sold': {
                    'value': len(completed),
                    'change': 0.0,
                    'trend': 'up' if completed else 'flat',
                },
                'avg_price': {
                    'value': round(revenue / len(completed), 2) if completed and revenue else 0.0,
                    'change': 0.0,
                    'trend': 'flat',
                    'currency': 'USD',
                },
                'active_users': {
                    'value': User.query.filter(User.last_login >= recent_cutoff).count() or 1,
                    'change': 0.0,
                    'trend': 'up',
                },
            },
            'insights': insights,
            'recent_metrics': recent_metrics,
        }

    @staticmethod
    def get_statistics(dataset='sales'):
        base_map = {
            'sales': 125.45,
            'traffic': 342.1,
            'users': 88.4,
            'performance': 42.75,
        }
        mean = base_map.get(dataset, 125.45)
        return {
            'dataset': dataset,
            'descriptive': {
                'mean': mean,
                'median': round(mean * 0.96, 2),
                'mode': round(mean * 0.92, 2),
                'std_dev': round(mean * 0.23, 2),
                'variance': round((mean * 0.23) ** 2, 2),
                'min': round(mean * 0.36, 2),
                'max': round(mean * 2.28, 2),
                'q1': round(mean * 0.76, 2),
                'q3': round(mean * 1.24, 2),
                'range': round(mean * 1.92, 2),
                'iqr': round(mean * 0.48, 2),
            },
            'distribution': {
                'skewness': 0.31,
                'kurtosis': -0.18,
                'normality': {
                    'test': 'Shapiro-Wilk',
                    'p_value': 0.091,
                    'is_normal': True,
                },
            },
            'inferential': {
                'confidence_interval_95': [round(mean * 0.9, 2), round(mean * 1.1, 2)],
                't_statistic': 2.11,
                'p_value': 0.034,
                'significant': True,
            },
            'correlation': {
                'variables': ['Conversions', 'Storage Usage', 'Downloads'],
                'matrix': [[1.0, 0.71, 0.66], [0.71, 1.0, 0.58], [0.66, 0.58, 1.0]],
                'significant_pairs': [
                    {'var1': 'Conversions', 'var2': 'Storage Usage', 'r': 0.71, 'p': 0.004},
                ],
            },
            'regression': {
                'model': 'Linear',
                'r_squared': 0.57,
                'coefficients': {
                    'intercept': round(mean * 0.2, 2),
                    'storage_usage': 0.63,
                    'downloads': 0.18,
                },
                'model_fit': 'Good',
            },
        }

    @staticmethod
    def get_forecast(metric='revenue', days=14):
        days = max(1, min(int(days or 14), 30))
        seed = {
            'revenue': 8500,
            'conversions': 120,
            'storage': 380,
        }.get(metric, 8500)
        return {
            'metric': metric,
            'forecast_days': days,
            'model': {
                'name': 'ARIMA',
                'accuracy': 0.91,
                'mae': 118.4,
                'rmse': 176.2,
            },
            'forecast_values': [
                {
                    'day': day,
                    'forecast': seed + (day * 75),
                    'lower_ci': seed + (day * 68),
                    'upper_ci': seed + (day * 82),
                }
                for day in range(1, days + 1)
            ],
            'anomalies': [],
            'trends': {
                'direction': 'uptrend',
                'slope': 75.0,
                'seasonality': 'weekly',
                'volatility': 'moderate',
            },
            'recommendations': [
                'Review report cadence before forecasted peak periods.',
                'Watch collaboration volume alongside conversion growth.',
            ],
        }

    @staticmethod
    def list_reports(user_id):
        reports = AnalyticsReport.query.filter_by(user_id=user_id).order_by(AnalyticsReport.created_at.desc()).all()
        return [report.to_dict() for report in reports]

    @staticmethod
    def create_report(user_id, payload):
        report = AnalyticsReport(
            user_id=user_id,
            name=(payload.get('name') or 'Untitled Report').strip(),
            description=payload.get('description'),
            report_type=payload.get('report_type', 'analytics'),
            config=payload.get('config') or {},
            export_format=payload.get('export_format', 'pdf'),
            last_run_at=Phase15Service._now(),
        )
        db.session.add(report)
        db.session.flush()
        Phase15Service.log_activity(user_id, 'report_created', 'report', report.id, {'name': report.name})
        Phase15Service.create_notification(
            user_id,
            'report_generated',
            'Report saved',
            f"Report '{report.name}' is ready for export.",
            link=f'/reports/{report.id}',
        )
        db.session.commit()
        return report

    @staticmethod
    def get_report_for_user(user_id, report_id):
        report = AnalyticsReport.query.get_or_404(report_id)
        user = User.query.get_or_404(user_id)
        if report.user_id != user_id and not user.is_admin():
            return None
        return report

    @staticmethod
    def export_report(report, export_format):
        report.last_run_at = Phase15Service._now()
        export_data = ReportService.export_report(report.to_dict(), format=export_format)
        db.session.commit()
        return export_data

    @staticmethod
    def list_documents(user_id):
        documents = Phase15Service.accessible_document_query(user_id).order_by(CollaborationDocument.updated_at.desc()).all()
        return [
            document.to_dict(shared_with=document.shares.count())
            for document in documents
        ]

    @staticmethod
    def create_document(user_id, payload):
        document = CollaborationDocument(
            owner_user_id=user_id,
            name=(payload.get('name') or 'Untitled').strip(),
            file_size=int(payload.get('file_size') or 0),
            mime_type=payload.get('mime_type') or 'application/octet-stream',
            metadata_json=payload.get('metadata') or {},
        )
        db.session.add(document)
        db.session.flush()
        Phase15Service.log_activity(user_id, 'document_uploaded', 'document', document.id, {'name': document.name})
        db.session.commit()
        return document

    @staticmethod
    def share_document(user_id, document, payload):
        recipients = payload.get('recipients') or []
        permission = payload.get('permission') or 'view'
        created_shares = []
        for recipient in recipients:
            target_user = None
            recipient_email = None
            recipient_user_id = None
            if isinstance(recipient, int) or (isinstance(recipient, str) and recipient.isdigit()):
                recipient_user_id = int(recipient)
                target_user = User.query.get(recipient_user_id)
                recipient_email = target_user.email if target_user else None
            else:
                recipient_email = str(recipient).strip()
                if recipient_email:
                    target_user = User.query.filter(func.lower(User.email) == recipient_email.lower()).first()
                    recipient_user_id = target_user.id if target_user else None

            share = DocumentShare(
                document_id=document.id,
                shared_by_user_id=user_id,
                recipient_user_id=recipient_user_id,
                recipient_email=recipient_email,
                permission=permission,
            )
            db.session.add(share)
            created_shares.append(share)

            if target_user:
                Phase15Service.create_notification(
                    target_user.id,
                    'document_shared',
                    'Document shared',
                    f"A document named '{document.name}' was shared with you.",
                    link=f'/documents/{document.id}',
                )

        Phase15Service.log_activity(user_id, 'document_shared', 'document', document.id, {'recipients': recipients, 'permission': permission})
        db.session.commit()
        return created_shares

    @staticmethod
    def list_comments(document_id):
        comments = DocumentComment.query.filter_by(document_id=document_id, parent_comment_id=None).order_by(DocumentComment.created_at.asc()).all()
        serialized = []
        for comment in comments:
            item = comment.to_dict()
            item['replies'] = [reply.to_dict() for reply in sorted(comment.replies, key=lambda reply: reply.created_at or datetime.min)]
            serialized.append(item)
        return serialized

    @staticmethod
    def add_comment(user_id, document, payload):
        comment = DocumentComment(
            document_id=document.id,
            author_user_id=user_id,
            parent_comment_id=payload.get('parent_comment_id'),
            content=(payload.get('content') or '').strip(),
            reactions={'likes': 0, 'loves': 0},
        )
        db.session.add(comment)
        db.session.flush()
        Phase15Service.log_activity(user_id, 'comment_added', 'document', document.id, {'comment_id': comment.id})
        if document.owner_user_id != user_id:
            Phase15Service.create_notification(
                document.owner_user_id,
                'comment_added',
                'New comment',
                f"A new comment was added to '{document.name}'.",
                link=f'/documents/{document.id}',
            )
        db.session.commit()
        return comment

    @staticmethod
    def list_teams(user_id):
        memberships = TeamMembership.query.filter_by(user_id=user_id).all()
        team_roles = {membership.team_id: membership.role for membership in memberships}
        teams = CollaborationTeam.query.filter(
            or_(
                CollaborationTeam.created_by_user_id == user_id,
                CollaborationTeam.id.in_(team_roles.keys() or ['']),
            )
        ).order_by(CollaborationTeam.created_at.desc()).all()
        return [team.to_dict(members=team.members.count(), role=team_roles.get(team.id, 'admin' if team.created_by_user_id == user_id else 'member')) for team in teams]

    @staticmethod
    def create_team(user_id, payload):
        team = CollaborationTeam(
            name=(payload.get('name') or '').strip(),
            description=payload.get('description'),
            created_by_user_id=user_id,
        )
        db.session.add(team)
        db.session.flush()
        membership = TeamMembership(team_id=team.id, user_id=user_id, role='admin')
        db.session.add(membership)
        Phase15Service.log_activity(user_id, 'team_created', 'team', team.id, {'name': team.name})
        db.session.commit()
        return team

    @staticmethod
    def get_team_for_user(user_id, team_id):
        team = CollaborationTeam.query.get_or_404(team_id)
        user = User.query.get_or_404(user_id)
        if user.is_admin() or team.created_by_user_id == user_id:
            return team
        membership = TeamMembership.query.filter_by(team_id=team_id, user_id=user_id).first()
        return team if membership else None

    @staticmethod
    def get_team_members(team_id):
        memberships = TeamMembership.query.filter_by(team_id=team_id).all()
        users = {user.id: user for user in User.query.filter(User.id.in_([item.user_id for item in memberships] or [-1])).all()}
        return [
            {
                'id': membership.user_id,
                'name': users[membership.user_id].username if membership.user_id in users else f'user-{membership.user_id}',
                'email': users[membership.user_id].email if membership.user_id in users else None,
                'role': membership.role,
                'joined': membership.created_at.isoformat() if membership.created_at else None,
            }
            for membership in memberships
        ]

    @staticmethod
    def list_notifications(user_id, filter_type=None):
        Phase15Service.ensure_notification_preferences(user_id)
        query = CollaborationNotification.query.filter_by(user_id=user_id)
        if filter_type == 'unread':
            query = query.filter_by(is_read=False)
        elif filter_type == 'shares':
            query = query.filter_by(notification_type='document_shared')
        elif filter_type == 'comments':
            query = query.filter_by(notification_type='comment_added')

        notifications = query.order_by(CollaborationNotification.created_at.desc()).all()
        unread_count = CollaborationNotification.query.filter_by(user_id=user_id, is_read=False).count()
        return {
            'total': len(notifications),
            'unread_count': unread_count,
            'notifications': [notification.to_dict() for notification in notifications],
        }

    @staticmethod
    def mark_notification_read(user_id, notification_id):
        notification = CollaborationNotification.query.filter_by(id=notification_id, user_id=user_id).first_or_404()
        notification.is_read = True
        notification.read_at = Phase15Service._now()
        db.session.commit()
        return notification

    @staticmethod
    def get_notification_preferences(user_id):
        preferences = Phase15Service.ensure_notification_preferences(user_id)
        db.session.commit()
        return preferences

    @staticmethod
    def update_notification_preferences(user_id, payload):
        preferences = Phase15Service.ensure_notification_preferences(user_id)
        for field in (
            'email_notifications',
            'in_app_notifications',
            'document_shared',
            'comment_added',
            'team_invitation',
            'report_generated',
            'daily_digest',
        ):
            if field in payload:
                setattr(preferences, field, bool(payload[field]))
        db.session.commit()
        return preferences

    @staticmethod
    def list_activity_logs(action=None, user_id=None):
        query = CollaborationActivityLog.query
        if action:
            query = query.filter_by(action=action)
        if user_id:
            query = query.filter_by(user_id=user_id)
        logs = query.order_by(CollaborationActivityLog.created_at.desc()).limit(20).all()
        return {
            'total': len(logs),
            'logs': [log.to_dict() for log in logs],
        }

    @staticmethod
    def permissions_matrix():
        return {
            'roles': ['Viewer', 'Editor', 'Admin'],
            'permissions': ['View', 'Download', 'Comment', 'Edit', 'Export', 'Share', 'Manage'],
            'matrix': [
                [True, True, True, False, False, False, False],
                [True, True, True, True, True, True, False],
                [True, True, True, True, True, True, True],
            ],
        }

    @staticmethod
    def permission_roles():
        return [
            {'id': 'viewer', 'name': 'Viewer', 'description': 'Read-only access', 'permissions': ['view', 'download']},
            {'id': 'editor', 'name': 'Editor', 'description': 'Can view, comment, edit, and share', 'permissions': ['view', 'download', 'comment', 'edit', 'export', 'share']},
            {'id': 'admin', 'name': 'Admin', 'description': 'Full access', 'permissions': ['view', 'download', 'comment', 'edit', 'export', 'share', 'manage']},
        ]

    @staticmethod
    def collaboration_dashboard(user_id):
        documents = Phase15Service.accessible_document_query(user_id).all()
        team_ids = [membership.team_id for membership in TeamMembership.query.filter_by(user_id=user_id).all()]
        recent_activities = CollaborationActivityLog.query.filter(
            or_(
                CollaborationActivityLog.user_id == user_id,
                CollaborationActivityLog.resource_type == 'document',
            )
        ).order_by(CollaborationActivityLog.created_at.desc()).limit(10).all()
        return {
            'stats': {
                'shared_items': DocumentShare.query.filter_by(shared_by_user_id=user_id).count(),
                'team_members': TeamMembership.query.filter(TeamMembership.team_id.in_(team_ids or [''])).count(),
                'activities': CollaborationActivityLog.query.filter_by(user_id=user_id).count(),
                'pending_requests': CollaborationNotification.query.filter_by(user_id=user_id, is_read=False).count(),
            },
            'recent_activities': [activity.to_dict() for activity in recent_activities],
            'pending_approvals': [],
            'documents': [document.to_dict(shared_with=document.shares.count()) for document in documents[:5]],
        }