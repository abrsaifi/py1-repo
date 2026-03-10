"""
Phase 15.3: Email Notification System
Handles email notifications for document sharing, comments, mentions, and alerts
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ========== EMAIL CONFIGURATION ==========
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Change to your SMTP server
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',  # Change this
    'sender_password': 'your-app-password',  # Change this
    'from_name': 'DocPro Analytics'
}

# In-memory queue for notifications
email_queue: List[Dict] = []
sent_emails: Dict[str, Dict] = {}  # {email_id: email_info}

# ========== EMAIL TEMPLATES ==========
class EmailTemplate(ABC):
    """Base class for email templates"""
    
    @abstractmethod
    def get_subject(self) -> str:
        pass
    
    @abstractmethod
    def get_html_body(self) -> str:
        pass
    
    @abstractmethod
    def get_text_body(self) -> str:
        pass


class DocumentSharedTemplate(EmailTemplate):
    """Email template for document sharing"""
    
    def __init__(self, recipient_name: str, sharer_name: str, document_name: str, 
                 permission: str, document_url: str):
        self.recipient_name = recipient_name
        self.sharer_name = sharer_name
        self.document_name = document_name
        self.permission = permission
        self.document_url = document_url
    
    def get_subject(self) -> str:
        return f"📄 {self.sharer_name} shared '{self.document_name}' with you"
    
    def get_html_body(self) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2>Document Shared with You</h2>
                    <p>Hi {self.recipient_name},</p>
                    <p><strong>{self.sharer_name}</strong> shared a document with you:</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>{self.document_name}</h3>
                        <p><strong>Permission:</strong> {self.permission}</p>
                    </div>
                    
                    <p>
                        <a href="{self.document_url}" style="
                            background: #007bff;
                            color: white;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px;
                            display: inline-block;
                        ">View Document</a>
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        © {datetime.now().year} DocPro Analytics. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
    
    def get_text_body(self) -> str:
        return f"""
        Document Shared with You
        
        Hi {self.recipient_name},
        
        {self.sharer_name} shared a document with you:
        
        Document: {self.document_name}
        Permission: {self.permission}
        
        View it here: {self.document_url}
        
        Best regards,
        DocPro Analytics Team
        """


class CommentMentionTemplate(EmailTemplate):
    """Email template for comment mentions"""
    
    def __init__(self, recipient_name: str, commenter_name: str, document_name: str, 
                 comment_preview: str, document_url: str):
        self.recipient_name = recipient_name
        self.commenter_name = commenter_name
        self.document_name = document_name
        self.comment_preview = comment_preview
        self.document_url = document_url
    
    def get_subject(self) -> str:
        return f"💬 {self.commenter_name} mentioned you in '{self.document_name}'"
    
    def get_html_body(self) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2>You've Been Mentioned</h2>
                    <p>Hi {self.recipient_name},</p>
                    <p><strong>{self.commenter_name}</strong> mentioned you in a comment on 
                       <strong>{self.document_name}</strong>:</p>
                    
                    <div style="background: #f0f8ff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
                        <p style="margin: 0;">"{self.comment_preview}"</p>
                    </div>
                    
                    <p>
                        <a href="{self.document_url}" style="
                            background: #007bff;
                            color: white;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px;
                            display: inline-block;
                        ">View Comment</a>
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        © {datetime.now().year} DocPro Analytics. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
    
    def get_text_body(self) -> str:
        return f"""
        You've Been Mentioned
        
        Hi {self.recipient_name},
        
        {self.commenter_name} mentioned you in a comment on {self.document_name}:
        
        "{self.comment_preview}"
        
        View it here: {self.document_url}
        
        Best regards,
        DocPro Analytics Team
        """


class TeamInvitationTemplate(EmailTemplate):
    """Email template for team invitations"""
    
    def __init__(self, recipient_name: str, inviter_name: str, team_name: str, 
                 join_url: str):
        self.recipient_name = recipient_name
        self.inviter_name = inviter_name
        self.team_name = team_name
        self.join_url = join_url
    
    def get_subject(self) -> str:
        return f"👥 {self.inviter_name} invited you to join '{self.team_name}'"
    
    def get_html_body(self) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2>Team Invitation</h2>
                    <p>Hi {self.recipient_name},</p>
                    <p><strong>{self.inviter_name}</strong> invited you to join the team:</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>{self.team_name}</h3>
                        <p>Join this team to collaborate with other members and access shared resources.</p>
                    </div>
                    
                    <p>
                        <a href="{self.join_url}" style="
                            background: #28a745;
                            color: white;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px;
                            display: inline-block;
                        ">Join Team</a>
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        © {datetime.now().year} DocPro Analytics. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
    
    def get_text_body(self) -> str:
        return f"""
        Team Invitation
        
        Hi {self.recipient_name},
        
        {self.inviter_name} invited you to join {self.team_name}
        
        Join here: {self.join_url}
        
        Best regards,
        DocPro Analytics Team
        """


class ReportGeneratedTemplate(EmailTemplate):
    """Email template for automated report notifications"""
    
    def __init__(self, recipient_name: str, report_name: str, download_url: str):
        self.recipient_name = recipient_name
        self.report_name = report_name
        self.download_url = download_url
    
    def get_subject(self) -> str:
        return f"📊 Your Report '{self.report_name}' is Ready"
    
    def get_html_body(self) -> str:
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2>Report Generated</h2>
                    <p>Hi {self.recipient_name},</p>
                    <p>Your requested report <strong>{self.report_name}</strong> is now ready for download.</p>
                    
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Report Name:</strong> {self.report_name}</p>
                        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                    </div>
                    
                    <p>
                        <a href="{self.download_url}" style="
                            background: #007bff;
                            color: white;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px;
                            display: inline-block;
                        ">Download Report</a>
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        © {datetime.now().year} DocPro Analytics. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
    
    def get_text_body(self) -> str:
        return f"""
        Report Generated
        
        Hi {self.recipient_name},
        
        Your report '{self.report_name}' is ready!
        
        Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}
        
        Download here: {self.download_url}
        
        Best regards,
        DocPro Analytics Team
        """


# ========== EMAIL SENDER ==========
class EmailSender:
    """Handles email sending"""
    
    def __init__(self, config: Dict = EMAIL_CONFIG):
        self.config = config
    
    def send_email(self, recipient_email: str, template: EmailTemplate) -> bool:
        """Send email with template"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.config['from_name']} <{self.config['sender_email']}>"
            message['To'] = recipient_email
            message['Subject'] = template.get_subject()
            
            # Attach HTML and text versions
            text_part = MIMEText(template.get_text_body(), 'plain')
            html_part = MIMEText(template.get_html_body(), 'html')
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(message)
            
            logger.info(f"Email sent to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            return False
    
    def queue_email(self, recipient_email: str, template: EmailTemplate) -> str:
        """Queue email for later sending"""
        email_id = f"email_{datetime.utcnow().timestamp()}"
        
        email_entry = {
            'id': email_id,
            'recipient': recipient_email,
            'subject': template.get_subject(),
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        email_queue.append(email_entry)
        sent_emails[email_id] = email_entry
        
        logger.info(f"Email queued: {email_id}")
        return email_id
    
    def get_queue_status(self) -> Dict:
        """Get email queue status"""
        return {
            'queue_size': len(email_queue),
            'total_sent': len([e for e in sent_emails.values() if e['status'] == 'sent']),
            'total_failed': len([e for e in sent_emails.values() if e['status'] == 'failed']),
            'pending': [e for e in email_queue if e['status'] == 'pending']
        }


# ========== NOTIFICATION TRIGGERS ==========
class NotificationTriggers:
    """Triggers for different notification events"""
    
    def __init__(self, sender: EmailSender):
        self.sender = sender
    
    def on_document_shared(self, recipient_email: str, recipient_name: str, 
                          sharer_name: str, document_name: str, 
                          permission: str, document_url: str):
        """Trigger when document is shared"""
        template = DocumentSharedTemplate(
            recipient_name, sharer_name, document_name, permission, document_url
        )
        return self.sender.send_email(recipient_email, template)
    
    def on_mention_comment(self, recipient_email: str, recipient_name: str, 
                          commenter_name: str, document_name: str, 
                          comment_preview: str, document_url: str):
        """Trigger when user is mentioned"""
        template = CommentMentionTemplate(
            recipient_name, commenter_name, document_name, comment_preview, document_url
        )
        return self.sender.send_email(recipient_email, template)
    
    def on_team_invitation(self, recipient_email: str, recipient_name: str, 
                          inviter_name: str, team_name: str, join_url: str):
        """Trigger when invited to team"""
        template = TeamInvitationTemplate(
            recipient_name, inviter_name, team_name, join_url
        )
        return self.sender.send_email(recipient_email, template)
    
    def on_report_generated(self, recipient_email: str, recipient_name: str, 
                           report_name: str, download_url: str):
        """Trigger when report is generated"""
        template = ReportGeneratedTemplate(recipient_name, report_name, download_url)
        return self.sender.send_email(recipient_email, template)


# ========== FLASK ROUTE HANDLERS ==========
def register_email_routes(app):
    """Register email notification routes"""
    from flask import request, jsonify
    
    sender = EmailSender()
    triggers = NotificationTriggers(sender)
    
    @app.route('/api/notifications/email/send', methods=['POST'])
    def send_notification_email():
        """Send email notification"""
        try:
            data = request.get_json()
            notification_type = data.get('type')  # share, mention, team, report
            recipient_email = data.get('recipient_email')
            
            if not all([notification_type, recipient_email]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            success = False
            
            if notification_type == 'share':
                success = triggers.on_document_shared(
                    recipient_email,
                    data.get('recipient_name'),
                    data.get('sharer_name'),
                    data.get('document_name'),
                    data.get('permission'),
                    data.get('document_url')
                )
            
            elif notification_type == 'mention':
                success = triggers.on_mention_comment(
                    recipient_email,
                    data.get('recipient_name'),
                    data.get('commenter_name'),
                    data.get('document_name'),
                    data.get('comment_preview'),
                    data.get('document_url')
                )
            
            elif notification_type == 'team':
                success = triggers.on_team_invitation(
                    recipient_email,
                    data.get('recipient_name'),
                    data.get('inviter_name'),
                    data.get('team_name'),
                    data.get('join_url')
                )
            
            elif notification_type == 'report':
                success = triggers.on_report_generated(
                    recipient_email,
                    data.get('recipient_name'),
                    data.get('report_name'),
                    data.get('download_url')
                )
            
            return jsonify({
                'success': success,
                'message': 'Email sent' if success else 'Failed to send email',
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200 if success else 500
        
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/notifications/email/queue', methods=['GET'])
    def get_email_queue():
        """Get email queue status"""
        try:
            status = sender.get_queue_status()
            return jsonify({
                'success': True,
                'data': status,
                'meta': {'timestamp': datetime.utcnow().isoformat()}
            }), 200
        
        except Exception as e:
            logger.error(f"Queue status error: {e}")
            return jsonify({'error': str(e)}), 500


# ========== EMAIL NOTIFICATION API REFERENCE ==========
"""
REST API ENDPOINTS:

1. Send Email Notification
   POST /api/notifications/email/send
   
   For Document Sharing:
   {
       "type": "share",
       "recipient_email": "user@example.com",
       "recipient_name": "John Smith",
       "sharer_name": "Jane Doe",
       "document_name": "Q4 Report",
       "permission": "view",
       "document_url": "https://app.example.com/documents/123"
   }
   
   For Comment Mention:
   {
       "type": "mention",
       "recipient_email": "user@example.com",
       "recipient_name": "John Smith",
       "commenter_name": "Jane Doe",
       "document_name": "Q4 Report",
       "comment_preview": "Great analysis! I think we should...",
       "document_url": "https://app.example.com/documents/123"
   }
   
   For Team Invitation:
   {
       "type": "team",
       "recipient_email": "user@example.com",
       "recipient_name": "John Smith",
       "inviter_name": "Jane Doe",
       "team_name": "Analytics Team",
       "join_url": "https://app.example.com/teams/456/join"
   }
   
   For Report Generated:
   {
       "type": "report",
       "recipient_email": "user@example.com",
       "recipient_name": "John Smith",
       "report_name": "Monthly Sales Report",
       "download_url": "https://app.example.com/reports/789/download"
   }

2. Get Email Queue Status
   GET /api/notifications/email/queue
   
   Response:
   {
       "success": true,
       "data": {
           "queue_size": 5,
           "total_sent": 42,
           "total_failed": 2,
           "pending": [...]
       }
   }

SETUP INSTRUCTIONS:

1. Configure SMTP settings in EMAIL_CONFIG:
   - smtp_server: Your SMTP server (e.g., smtp.gmail.com)
   - smtp_port: Your SMTP port (e.g., 587)
   - sender_email: Your email address
   - sender_password: Your app-specific password

2. For Gmail:
   - Enable 2-factor authentication
   - Generate app password at https://myaccount.google.com/apppasswords
   - Use app password in sender_password field

3. Test email sending:
   - Call POST /api/notifications/email/send with test data
   - Check email inbox for received message

EMAIL TEMPLATES:
1. DocumentSharedTemplate - For sharing notifications
2. CommentMentionTemplate - For comment mentions
3. TeamInvitationTemplate - For team invitations
4. ReportGeneratedTemplate - For automated reports
"""
