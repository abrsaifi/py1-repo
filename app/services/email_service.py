"""Email service for sending notifications."""
from collections import UserDict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app


class _SafeFormatDict(UserDict):
    def __missing__(self, key):
        return '{' + key + '}'


class EmailService:
    """Service for sending emails."""

    @staticmethod
    def _config_bool(value, default=False):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}

    @staticmethod
    def _from_address():
        return (
            current_app.config.get('MAIL_FROM')
            or current_app.config.get('MAIL_FROM_ADDRESS')
            or 'noreply@docpro.local'
        )

    @staticmethod
    def _smtp_settings():
        return {
            'host': current_app.config.get('SMTP_HOST') or current_app.config.get('MAIL_SERVER'),
            'port': int(current_app.config.get('SMTP_PORT') or current_app.config.get('MAIL_PORT') or 25),
            'username': current_app.config.get('SMTP_USERNAME') or current_app.config.get('MAIL_USERNAME'),
            'password': current_app.config.get('SMTP_PASSWORD') or current_app.config.get('MAIL_PASSWORD'),
            'use_tls': EmailService._config_bool(
                current_app.config.get('SMTP_USE_TLS', current_app.config.get('MAIL_USE_TLS')),
                default=False,
            ),
            'use_ssl': EmailService._config_bool(
                current_app.config.get('SMTP_USE_SSL', current_app.config.get('MAIL_USE_SSL')),
                default=False,
            ),
            'suppress_send': EmailService._config_bool(
                current_app.config.get('MAIL_SUPPRESS_SEND'),
                default=bool(current_app.config.get('TESTING')),
            ),
        }

    @staticmethod
    def _render_body(template=None, context=None, body=None, html=False):
        if body is not None:
            return body, html

        if isinstance(template, dict):
            rendered = template.get('html' if html else 'text')
            if rendered is None:
                rendered = template.get('body') or template.get('text') or template.get('html') or ''
            return rendered, html or ('html' in template and 'text' not in template)

        if isinstance(template, str):
            if context:
                return template.format_map(_SafeFormatDict(context)), html
            return template, html

        return '', html

    @staticmethod
    def send_email(to_address, subject, body, html=False):
        """Backward-compatible wrapper for sending a simple email message."""
        return EmailService().send(to=to_address, subject=subject, body=body, html=html)

    def send(self, to, subject, template=None, context=None, body=None, html=False):
        """Send an email message using either direct body content or a format string template."""
        try:
            rendered_body, rendered_html = self._render_body(template=template, context=context, body=body, html=html)

            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self._from_address()
            msg['To'] = to
            msg.attach(MIMEText(rendered_body, 'html' if rendered_html else 'plain'))

            settings = self._smtp_settings()
            if settings['suppress_send'] or not settings['host']:
                current_app.logger.info('Email send suppressed for %s: %s', to, subject)
                return True

            smtp_cls = smtplib.SMTP_SSL if settings['use_ssl'] else smtplib.SMTP
            with smtp_cls(settings['host'], settings['port']) as server:
                if settings['use_tls'] and not settings['use_ssl']:
                    server.starttls()
                if settings['username']:
                    server.login(settings['username'], settings['password'] or '')
                server.sendmail(msg['From'], [to], msg.as_string())

            current_app.logger.info('Email sent to %s: %s', to, subject)
            return True
        except Exception as exc:
            current_app.logger.error('Failed to send email: %s', exc)
            return False

    @staticmethod
    def send_password_reset(email, reset_token):
        """Send password reset email."""
        subject = 'Password Reset Request'
        body = f'Click here to reset your password: {reset_token}'
        return EmailService.send_email(email, subject, body)

    @staticmethod
    def send_notification(email, notification):
        """Send notification email."""
        return EmailService.send_email(email, notification['title'], notification['message'])
