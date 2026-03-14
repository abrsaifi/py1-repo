"""Persisted billing invoices for subscriptions."""
from datetime import datetime

from . import db
from app.utils.datetime_utils import utc_now_naive


class BillingInvoice(db.Model):
    """Invoice records for subscription billing events."""
    __tablename__ = 'billing_invoices'

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    ALLOWED_STATUSES = {STATUS_PENDING, STATUS_PAID, STATUS_FAILED, STATUS_REFUNDED}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False, index=True)
    invoice_number = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    plan_code = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(32), default='paid')
    issued_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    refunded_at = db.Column(db.DateTime)
    refund_amount = db.Column(db.Float)
    failure_code = db.Column(db.String(64))
    failure_reason = db.Column(db.String(255))
    gateway_reference_id = db.Column(db.String(128))
    processor_event_at = db.Column(db.DateTime)
    status_note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)
    audit_logs = db.relationship('BillingAuditLog', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'description': self.description,
            'plan_code': self.plan_code,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
            'refund_amount': self.refund_amount,
            'failure_code': self.failure_code,
            'failure_reason': self.failure_reason,
            'gateway_reference_id': self.gateway_reference_id,
            'processor_event_at': self.processor_event_at.isoformat() if self.processor_event_at else None,
            'status_note': self.status_note,
        }
