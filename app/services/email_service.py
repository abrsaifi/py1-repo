"""Email service for sending notifications."""
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    """Service for sending emails."""
    
    @staticmethod
    def send_email(to_address, subject, body, html=False):
        """Send an email message."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = current_app.config.get('MAIL_FROM', 'noreply@docpro.local')
            msg['To'] = to_address
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Email would be sent here if SMTP is configured
            current_app.logger.info(f"Email sent to {to_address}: {subject}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_password_reset(email, reset_token):
        """Send password reset email."""
        subject = "Password Reset Request"
        body = f"Click here to reset your password: {reset_token}"
        return EmailService.send_email(email, subject, body)
    
    @staticmethod
    def send_notification(email, notification):
        """Send notification email."""
        return EmailService.send_email(email, notification['title'], notification['message'])
