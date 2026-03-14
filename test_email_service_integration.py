from app import create_app
from app.models import Subscription, User, db
from app.services.email_service import EmailService
from app.services.reports import ReportService
from app.tasks import send_daily_reports, send_email as send_email_task


class _RetryCalled(Exception):
    pass


def _build_app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'email-test-secret',
        'JWT_SECRET_KEY': 'email-test-jwt-secret-key-0123456789',
        'ENABLE_BACKGROUND_TASKS': False,
        'MAIL_SUPPRESS_SEND': True,
        'MAIL_FROM_ADDRESS': 'noreply@test.local',
    })

    with app.app_context():
        db.create_all()

    return app


def test_email_service_send_uses_format_template_without_smtp():
    app = _build_app()

    with app.app_context():
        service = EmailService()
        result = service.send(
            to='user@example.com',
            subject='Hello',
            template='Hello {name}',
            context={'name': 'DocPro'},
        )

    assert result is True


def test_send_email_task_uses_email_service(monkeypatch):
    app = _build_app()
    captured = {}

    def fake_send(self, to, subject, template=None, context=None, body=None, html=False):
        captured['to'] = to
        captured['subject'] = subject
        captured['template'] = template
        captured['context'] = context
        return True

    with app.app_context():
        monkeypatch.setattr(EmailService, 'send', fake_send)
        result = send_email_task.run('ops@example.com', 'Status', 'Hello {name}', {'name': 'Ops'})

    assert result == {'status': 'sent', 'to': 'ops@example.com'}
    assert captured['to'] == 'ops@example.com'
    assert captured['subject'] == 'Status'
    assert captured['template'] == 'Hello {name}'
    assert captured['context'] == {'name': 'Ops'}


def test_report_service_can_send_daily_report(monkeypatch):
    app = _build_app()
    captured = {}

    def fake_send_email(to_address, subject, body, html=False):
        captured['to'] = to_address
        captured['subject'] = subject
        captured['body'] = body
        captured['html'] = html
        return True

    with app.app_context():
        user = User(
            email='daily@example.com',
            username='daily-user',
            password_hash='hashed',
            role='user',
        )
        db.session.add(user)
        db.session.commit()

        monkeypatch.setattr(EmailService, 'send_email', staticmethod(fake_send_email))
        result = ReportService.send_daily_report(user.id)

    assert result is True
    assert captured['to'] == 'daily@example.com'
    assert captured['subject'] == 'Your DocPro Daily Usage Report'
    assert 'daily-user' in captured['body']


def test_send_daily_reports_counts_active_subscriptions(monkeypatch):
    app = _build_app()

    with app.app_context():
        active_user = User(
            email='active@example.com',
            username='active-user',
            password_hash='hashed',
            role='user',
        )
        inactive_plan_user = User(
            email='inactive@example.com',
            username='inactive-user',
            password_hash='hashed',
            role='user',
        )
        no_plan_user = User(
            email='noplan@example.com',
            username='noplan-user',
            password_hash='hashed',
            role='user',
        )
        db.session.add_all([active_user, inactive_plan_user, no_plan_user])
        db.session.commit()

        db.session.add_all([
            Subscription(user_id=active_user.id, is_active=True),
            Subscription(user_id=inactive_plan_user.id, is_active=False),
        ])
        db.session.commit()

        sent_ids = []

        def fake_send_daily_report(user_id):
            sent_ids.append(user_id)
            return True

        monkeypatch.setattr(ReportService, 'send_daily_report', staticmethod(fake_send_daily_report))
        result = send_daily_reports.run()

    assert result == {'status': 'completed', 'users_notified': 1}
    assert sent_ids == [active_user.id]