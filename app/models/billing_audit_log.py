"""Audit trail for billing invoice status changes."""
from datetime import datetime

from . import db
from app.utils.datetime_utils import utc_now_naive


class BillingAuditLog(db.Model):
    """Record admin actions against persisted billing invoices."""
    __tablename__ = 'billing_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('billing_invoices.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    actor_username = db.Column(db.String(255), nullable=False)
    actor_email = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(100), nullable=False, default='invoice_status_updated')
    from_status = db.Column(db.String(32))
    to_status = db.Column(db.String(32), nullable=False)
    status_note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'actor_user_id': self.actor_user_id,
            'actor_username': self.actor_username,
            'actor_email': self.actor_email,
            'action': self.action,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'status_note': self.status_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }