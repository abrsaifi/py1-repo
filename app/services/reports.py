"""Report generation service."""
from flask import current_app
from datetime import datetime, timedelta, timezone

class ReportService:
    """Service for generating reports."""
    
    @staticmethod
    def generate_usage_report(user_id, days=30):
        """Generate usage report for a user."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        return {
            'user_id': user_id,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_documents': 0,
            'total_api_calls': 0,
            'total_storage_used': 0,
        }
    
    @staticmethod
    def generate_analytics_report(start_date, end_date):
        """Generate system analytics report."""
        return {
            'period_start': start_date.isoformat() if isinstance(start_date, datetime) else start_date,
            'period_end': end_date.isoformat() if isinstance(end_date, datetime) else end_date,
            'total_users': 0,
            'total_documents': 0,
            'total_api_calls': 0,
            'average_response_time': 0,
        }
    
    @staticmethod
    def generate_compliance_report(report_type='audit'):
        """Generate compliance report."""
        return {
            'report_type': report_type,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'status': 'compliant',
            'findings': [],
        }
    
    @staticmethod
    def export_report(report_data, format='pdf'):
        """Export report in specified format."""
        if format == 'pdf':
            return {'status': 'exported', 'format': 'pdf', 'url': '/reports/download'}
        elif format == 'csv':
            return {'status': 'exported', 'format': 'csv', 'url': '/reports/download'}
        else:
            return {'status': 'error', 'message': 'Unsupported format'}

    @staticmethod
    def send_daily_report(user_id):
        """Generate and send a simple daily usage report email to a user."""
        from app.models import User
        from app.models import db
        from app.services.email_service import EmailService

        user = db.session.get(User, user_id)
        if not user or not user.is_active or not user.email:
            current_app.logger.warning('Daily report skipped for user_id=%s', user_id)
            return False

        report = ReportService.generate_usage_report(user_id, days=1)
        subject = 'Your DocPro Daily Usage Report'
        body = (
            'Hello {username},\n\n'
            'Here is your daily DocPro summary.\n'
            'Period: {period_start} -> {period_end}\n'
            'Documents processed: {total_documents}\n'
            'API calls: {total_api_calls}\n'
            'Storage used: {total_storage_used}\n\n'
            'DocPro'
        ).format(
            username=user.username,
            period_start=report['period_start'],
            period_end=report['period_end'],
            total_documents=report['total_documents'],
            total_api_calls=report['total_api_calls'],
            total_storage_used=report['total_storage_used'],
        )
        return EmailService.send_email(user.email, subject, body)
