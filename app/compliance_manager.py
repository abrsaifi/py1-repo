"""
Compliance Manager - GDPR and SOC2 Compliance System
Handles audit logging, data deletion, encryption, and regulatory compliance
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import logging
import json
from uuid import UUID, uuid4
import os

logger = logging.getLogger(__name__)


class DataEncryption:
    """Handles encryption/decryption of sensitive data at rest"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption with master key
        If no key provided, generates from environment or creates new
        """
        if master_key:
            self.master_key = master_key.encode() if isinstance(master_key, str) else master_key
        else:
            # Try to load from environment
            env_key = os.environ.get('ENCRYPTION_KEY')
            if env_key:
                self.master_key = base64.urlsafe_b64decode(env_key)
            else:
                # Generate new key (for testing only - should use environment key in production)
                self.master_key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.master_key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data
        Returns: URL-safe base64 encoded encrypted text
        """
        try:
            if isinstance(data, str):
                data = data.encode()
            encrypted = self.cipher_suite.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data
        Returns: Original string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_pii(self, data: str, salt: Optional[str] = None) -> str:
        """
        One-way hash of PII (cannot be reversed, for anonymization)
        """
        try:
            if not salt:
                salt = os.urandom(16)
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(data.encode()))
            return key.decode()
        except Exception as e:
            logger.error(f"PII hashing failed: {e}")
            raise
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key for rotation"""
        return base64.urlsafe_b64encode(Fernet.generate_key()).decode()


class GDPRManager:
    """Manages GDPR compliance operations"""
    
    def __init__(self, db_session, encryption: Optional[DataEncryption] = None):
        self.db = db_session
        self.encryption = encryption or DataEncryption()
    
    def request_data_deletion(self, user_id: UUID, reason: str = "GDPR Article 17",
                             request_by: str = "user") -> UUID:
        """
        Create a GDPR right-to-be-forgotten request
        Returns: Request ID for tracking
        """
        try:
            from app.models.compliance import DataDeletionRequest
            
            request = DataDeletionRequest(
                user_id=user_id,
                requested_at=datetime.now(timezone.utc),
                requested_by=request_by,
                request_reason=reason,
                status='pending' if request_by == 'user' else 'approved',
                approval_required=(request_by == 'user'),
            )
            
            self.db.add(request)
            self.db.commit()
            
            logger.info(f"Data deletion requested for user {user_id}: {request.id}")
            return request.id
        except Exception as e:
            logger.error(f"Failed to create deletion request: {e}")
            self.db.rollback()
            raise
    
    def approve_deletion_request(self, request_id: UUID, admin_id: UUID) -> bool:
        """Approve a pending deletion request (requires admin)"""
        try:
            from app.models.compliance import DataDeletionRequest
            
            request = self.db.query(DataDeletionRequest).filter_by(id=request_id).first()
            if not request:
                raise ValueError(f"Request {request_id} not found")
            
            request.status = 'approved'
            request.approved_at = datetime.now(timezone.utc)
            request.approved_by = admin_id
            
            self.db.commit()
            logger.info(f"Deletion request {request_id} approved by {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to approve deletion: {e}")
            self.db.rollback()
            raise
    
    def execute_data_deletion(self, request_id: UUID) -> Tuple[bool, int, Optional[str]]:
        """
        Execute a deletion request
        Returns: (success, records_deleted, error_message)
        """
        try:
            from app.models.compliance import DataDeletionRequest, AuditLog
            from app.models.user import User
            from app.models.conversion import Conversion
            
            request = self.db.query(DataDeletionRequest).filter_by(id=request_id).first()
            if not request:
                return False, 0, "Request not found"
            
            if request.status != 'approved':
                return False, 0, "Request not approved"
            
            request.status = 'executing'
            request.started_at = datetime.now(timezone.utc)
            self.db.commit()
            
            total_deleted = 0
            deletion_details = {}
            
            try:
                # Delete user personal data (but keep user record for audit trail)
                user = self.db.query(User).filter_by(id=request.user_id).first()
                if user:
                    # Anonymize instead of delete to preserve audit trail
                    old_email = user.email
                    user.email = f"deleted-{uuid4().hex[:8]}@deleted.local"
                    user.first_name = "[DELETED]"
                    user.last_name = "[DELETED]"
                    user.phone = None
                    user.is_active = False
                    self.db.commit()
                    deletion_details['user'] = {'anonymized': True, 'old_email': self.encryption.encrypt(old_email)}
                    total_deleted += 1
                    request.data_categories.append('personal_info')
                
                # Delete conversion history
                conversions = self.db.query(Conversion).filter_by(user_id=request.user_id).all()
                for conversion in conversions:
                    self.db.delete(conversion)
                self.db.commit()
                if conversions:
                    deletion_details['conversions'] = {'count': len(conversions), 'deleted_at': datetime.now(timezone.utc).isoformat()}
                    total_deleted += len(conversions)
                    request.data_categories.append('conversion_history')
                
                # Soft-delete usage data (keep for audit but mark as deleted)
                from app.models.audit_log import DataAccessLog
                access_logs = self.db.query(DataAccessLog).filter_by(subject_user_id=request.user_id).all()
                for log in access_logs:
                    # Anonymize access logs
                    log.accessor_id = None
                    log.fields_accessed = []
                self.db.commit()
                if access_logs:
                    deletion_details['access_logs'] = {'count': len(access_logs), 'anonymized': True}
                    request.data_categories.append('usage_data')
                
                # Mark request as completed
                request.status = 'completed'
                request.completed_at = datetime.now(timezone.utc)
                request.total_records_deleted = total_deleted
                request.fields_deleted = deletion_details
                request.confirmation_sent = True
                request.confirmation_sent_at = datetime.now(timezone.utc)
                
                self.db.commit()
                
                logger.warning(f"Deletion request {request_id} completed: {total_deleted} records")
                return True, total_deleted, None
                
            except Exception as e:
                request.status = 'failed'
                request.error_message = str(e)
                self.db.commit()
                logger.error(f"Deletion execution failed: {e}")
                return False, total_deleted, str(e)
                
        except Exception as e:
            logger.error(f"Failed to execute deletion: {e}")
            return False, 0, str(e)
    
    def export_user_data(self, user_id: UUID) -> Dict:
        """
        Export all personal data for a user (GDPR Article 15)
        Returns: Dictionary of all user data
        """
        try:
            from app.models.user import User
            from app.models.conversion import Conversion
            from app.models.audit_log import DataAccessLog
            
            user = self.db.query(User).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            data_export = {
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                },
                'conversions': [],
                'access_history': [],
            }
            
            # Export conversions
            conversions = self.db.query(Conversion).filter_by(user_id=user_id).all()
            for conv in conversions:
                data_export['conversions'].append({
                    'id': str(conv.id),
                    'status': conv.status,
                    'input_format': conv.input_format,
                    'output_format': conv.output_format,
                    'created_at': conv.created_at.isoformat() if conv.created_at else None,
                })
            
            # Export data access logs
            access_logs = self.db.query(DataAccessLog).filter_by(subject_user_id=user_id).all()
            for log in access_logs:
                data_export['access_history'].append({
                    'timestamp': log.timestamp.isoformat(),
                    'accessor_type': log.accessor_type,
                    'data_category': log.data_category,
                    'access_reason': log.access_reason,
                })
            
            logger.info(f"Data export generated for user {user_id}")
            return data_export
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            raise
    
    def get_user_consents(self, user_id: UUID) -> Dict[str, bool]:
        """Get all consent preferences for a user"""
        try:
            from app.models.compliance import UserConsent
            
            consent = self.db.query(UserConsent).filter_by(
                user_id=user_id,
            ).order_by(UserConsent.consented_at.desc()).first()
            
            if not consent:
                return {
                    'data_processing': False,
                    'marketing': False,
                    'analytics': False,
                    'third_party_sharing': False,
                }
            
            return {
                'data_processing': consent.data_processing and not consent.withdrawn_at,
                'marketing': consent.marketing and not consent.withdrawn_at,
                'analytics': consent.analytics and not consent.withdrawn_at,
                'third_party_sharing': consent.third_party_sharing and not consent.withdrawn_at,
            }
        except Exception as e:
            logger.error(f"Failed to get user consents: {e}")
            return {}
    
    def update_user_consent(self, user_id: UUID, **consent_fields) -> bool:
        """Update user consent preferences"""
        try:
            from app.models.compliance import UserConsent
            
            consent = UserConsent(
                user_id=user_id,
                data_processing=consent_fields.get('data_processing', False),
                marketing=consent_fields.get('marketing', False),
                analytics=consent_fields.get('analytics', False),
                third_party_sharing=consent_fields.get('third_party_sharing', False),
                consent_method=consent_fields.get('consent_method', 'api'),
                ip_address=consent_fields.get('ip_address'),
                user_agent=consent_fields.get('user_agent'),
            )
            
            self.db.add(consent)
            self.db.commit()
            logger.info(f"Consent updated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update consent: {e}")
            self.db.rollback()
            return False
    
    def withdraw_all_consent(self, user_id: UUID) -> bool:
        """Withdraw all consent (right to withdraw under GDPR)"""
        try:
            from app.models.compliance import UserConsent
            
            # Find latest consent record
            consent = self.db.query(UserConsent).filter_by(
                user_id=user_id
            ).order_by(UserConsent.consented_at.desc()).first()
            
            if consent:
                consent.withdrawn_at = datetime.now(timezone.utc)
                self.db.commit()
            
            logger.info(f"All consent withdrawn for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            self.db.rollback()
            return False


class AuditLogger:
    """Helper for consistent audit logging throughout the application"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def log_event(self, event_type: str, event_category: str, action: str,
                 actor_id: UUID, actor_type: str = 'user',
                 resource_type: Optional[str] = None,
                 resource_id: Optional[UUID] = None,
                 result: str = 'success',
                 status_code: Optional[int] = None,
                 error_message: Optional[str] = None,
                 ip_address: Optional[str] = None,
                 gdpr_relevant: bool = False,
                 pii_involved: bool = False,
                 extra_data: Optional[Dict] = None) -> Optional[UUID]:
        """
        Log an audit event
        Returns: Audit log ID
        """
        try:
            from app.models.compliance import create_audit_log
            
            audit = create_audit_log(
                event_type=event_type,
                event_category=event_category,
                action=action,
                actor_id=actor_id,
                actor_type=actor_type,
                resource_type=resource_type,
                resource_id=resource_id,
                result=result,
                ip_address=ip_address,
                status_code=status_code,
                error_message=error_message,
                gdpr_relevant=gdpr_relevant,
                pii_involved=pii_involved,
            )
            
            if extra_data:
                audit.data_modified = extra_data
            
            self.db.add(audit)
            self.db.commit()
            
            return audit.id
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            self.db.rollback()
            return None
    
    def log_data_access(self, subject_user_id: UUID, accessor_id: Optional[UUID],
                       accessor_type: str, data_category: str,
                       fields_accessed: List[str],
                       access_method: str = 'api',
                       access_reason: str = 'normal_operation'):
        """Log data access for GDPR accountability"""
        try:
            from app.models.compliance import DataAccessLog
            
            log = DataAccessLog(
                subject_user_id=subject_user_id,
                accessor_id=accessor_id,
                accessor_type=accessor_type,
                data_category=data_category,
                fields_accessed=fields_accessed,
                access_method=access_method,
                access_reason=access_reason,
            )
            
            self.db.add(log)
            self.db.commit()
            return log.id
        except Exception as e:
            logger.error(f"Failed to log data access: {e}")
            self.db.rollback()
            return None
    
    def get_audit_trail(self, resource_type: Optional[str] = None,
                       resource_id: Optional[UUID] = None,
                       actor_id: Optional[UUID] = None,
                       period_days: int = 90,
                       limit: int = 100) -> List[Dict]:
        """Get audit trail for investigation"""
        try:
            from app.models.compliance import AuditLog
            
            query = self.db.query(AuditLog)
            
            if resource_type:
                query = query.filter_by(resource_type=resource_type)
            if resource_id:
                query = query.filter_by(resource_id=resource_id)
            if actor_id:
                query = query.filter_by(actor_id=actor_id)
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=period_days)
            query = query.filter(AuditLog.timestamp >= cutoff_time)
            
            logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    'timestamp': log.timestamp.isoformat(),
                    'event_type': log.event_type,
                    'action': log.action,
                    'actor': f"{log.actor_type}:{log.actor_id}",
                    'resource': f"{log.resource_type}:{log.resource_id}",
                    'result': log.result,
                    'error': log.error_message,
                }
                for log in logs
            ]
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []
    
    def cleanup_expired_logs(self) -> int:
        """Delete audit logs past their retention date"""
        try:
            from app.models.compliance import AuditLog
            
            count = self.db.query(AuditLog).filter(
                AuditLog.retention_until < datetime.now(timezone.utc)
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {count} expired audit logs")
            return count
        except Exception as e:
            logger.error(f"Failed to cleanup audit logs: {e}")
            self.db.rollback()
            return 0


class ComplianceReporter:
    """Generate compliance reports for audits and regulatory requirements"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def generate_gdpr_report(self, period_days: int = 30) -> Dict:
        """Generate GDPR compliance report"""
        try:
            from app.models.compliance import (
                AuditLog, DataDeletionRequest, UserConsent, DataAccessLog
            )
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=period_days)
            
            # Count GDPR-relevant events
            gdpr_events = self.db.query(AuditLog).filter(
                AuditLog.gdpr_relevant == True,
                AuditLog.timestamp >= cutoff_time
            ).count()
            
            # Count data deletion requests
            deletion_requests = self.db.query(DataDeletionRequest).filter(
                DataDeletionRequest.requested_at >= cutoff_time
            ).all()
            
            # Count data access logs
            access_logs = self.db.query(DataAccessLog).filter(
                DataAccessLog.timestamp >= cutoff_time
            ).count()
            
            # Count active consents
            active_consents = self.db.query(UserConsent).filter(
                UserConsent.consented_at >= cutoff_time,
                UserConsent.withdrawn_at == None
            ).count()
            
            return {
                'report_type': 'GDPR Compliance',
                'period_days': period_days,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'metrics': {
                    'gdpr_relevant_events': gdpr_events,
                    'deletion_requests': {
                        'total': len(deletion_requests),
                        'completed': sum(1 for r in deletion_requests if r.status == 'completed'),
                        'pending': sum(1 for r in deletion_requests if r.status == 'pending'),
                    },
                    'data_access_logs': access_logs,
                    'active_consents': active_consents,
                }
            }
        except Exception as e:
            logger.error(f"Failed to generate GDPR report: {e}")
            return {'error': str(e)}
    
    def generate_soc2_report(self) -> Dict:
        """Generate SOC2 compliance status report"""
        try:
            from app.models.compliance import SOC2Checkpoint
            
            checkpoints = self.db.query(SOC2Checkpoint).all()
            
            status_counts = {
                'passed': sum(1 for c in checkpoints if c.status == 'passed'),
                'pending': sum(1 for c in checkpoints if c.status == 'pending'),
                'failed': sum(1 for c in checkpoints if c.status == 'failed'),
            }
            
            return {
                'report_type': 'SOC2 Compliance',
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'total_checkpoints': len(checkpoints),
                'status': status_counts,
                'completion_percentage': (status_counts['passed'] / len(checkpoints) * 100) if checkpoints else 0,
                'checkpoints': [
                    {
                        'name': c.checkpoint_name,
                        'status': c.status,
                        'trust_service': c.trust_service,
                    }
                    for c in checkpoints
                ]
            }
        except Exception as e:
            logger.error(f"Failed to generate SOC2 report: {e}")
            return {'error': str(e)}


# Flask integration helper

def get_compliance_manager(db_session):
    """Get GDPR manager instance"""
    return GDPRManager(db_session)


def get_audit_logger(db_session):
    """Get audit logger instance"""
    return AuditLogger(db_session)


def get_compliance_reporter(db_session):
    """Get compliance reporter instance"""
    return ComplianceReporter(db_session)
