"""Persisted billing profile metadata for subscriber payment details."""
from datetime import datetime

from . import db
from app.utils.datetime_utils import utc_now_naive


class BillingProfile(db.Model):
    """Store user-managed billing details until an external billing provider is connected."""
    __tablename__ = 'billing_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    card_brand = db.Column(db.String(64), default='No card on file')
    card_last4 = db.Column(db.String(4), default='----')
    card_expiry_month = db.Column(db.Integer)
    card_expiry_year = db.Column(db.Integer)
    card_holder = db.Column(db.String(255))
    payment_status = db.Column(db.String(255), default='No payment data available.')
    billing_name = db.Column(db.String(255))
    billing_line1 = db.Column(db.String(255))
    billing_line2 = db.Column(db.String(255))
    billing_country = db.Column(db.String(100))
    tax_id = db.Column(db.String(100))
    tax_exemption = db.Column(db.String(100), default='Not applicable')
    created_at = db.Column(db.DateTime, default=utc_now_naive, nullable=False)
    updated_at = db.Column(db.DateTime, default=utc_now_naive, onupdate=utc_now_naive)

    @property
    def expiry_label(self):
        if not self.card_expiry_month or not self.card_expiry_year:
            return 'N/A'
        return f'{int(self.card_expiry_month):02d}/{int(self.card_expiry_year)}'

    def to_payment_dict(self):
        return {
            'method': {
                'brand': self.card_brand or 'No card on file',
                'last4': self.card_last4 or '----',
                'expiry': self.expiry_label,
                'holder': self.card_holder or self.billing_name or 'N/A',
                'status': self.payment_status or 'No payment data available.',
            },
            'billingAddress': {
                'name': self.billing_name or 'N/A',
                'line1': self.billing_line1 or 'N/A',
                'line2': self.billing_line2 or '',
                'country': self.billing_country or 'N/A',
            },
            'taxInfo': {
                'taxId': self.tax_id or 'Not provided',
                'taxExemption': self.tax_exemption or 'Not applicable',
            },
        }
