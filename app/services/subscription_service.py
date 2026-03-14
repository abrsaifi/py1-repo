"""Subscription and billing dashboard payload helpers."""
from datetime import datetime, timedelta, timezone
from io import BytesIO

from app.models import BillingInvoice, BillingProfile, Conversion, Subscription, User, db


class SubscriptionService:
    PLAN_CATALOG = {
        'free': {
            'name': 'Free',
            'price': 0.0,
            'period': 'forever',
            'description': 'Perfect for getting started',
            'features': ['10 conversions/day', '2 GB storage', 'Basic analytics', 'Email support'],
            'storage_quota_gb': 2,
            'monthly_conversion_limit': 300,
            'max_file_size_mb': 25,
            'cta': 'Downgrade',
        },
        'pro': {
            'name': 'Pro',
            'price': 9.99,
            'period': 'month',
            'description': 'For regular users',
            'features': ['Unlimited conversions', '100 GB storage', 'Advanced analytics', 'Priority support', 'API access', 'Custom branding'],
            'storage_quota_gb': 100,
            'monthly_conversion_limit': 5000,
            'max_file_size_mb': 250,
            'cta': 'Current Plan',
        },
        'enterprise': {
            'name': 'Enterprise',
            'price': None,
            'period': 'month',
            'description': 'For teams & enterprises',
            'features': ['Everything in Pro', '1 TB+ storage', 'Dedicated account manager', 'Phone support', 'Custom integrations', 'SLA guarantee'],
            'storage_quota_gb': 1024,
            'monthly_conversion_limit': 50000,
            'max_file_size_mb': 1024,
            'cta': 'Contact Sales',
        },
    }

    SELF_SERVE_PLANS = {'free', 'pro'}

    @staticmethod
    def _ensure_subscription(user):
        subscription = user.subscription
        if subscription:
            return subscription

        plan_code = (user.plan or 'free').lower()
        plan_meta = SubscriptionService.PLAN_CATALOG.get(plan_code, SubscriptionService.PLAN_CATALOG['free'])
        subscription = Subscription(
            user_id=user.id,
            plan=plan_code,
            storage_quota_gb=plan_meta['storage_quota_gb'],
            monthly_conversion_limit=plan_meta['monthly_conversion_limit'],
            max_file_size_mb=plan_meta['max_file_size_mb'],
            price_per_month=plan_meta['price'] or 0.0,
            is_active=True,
            auto_renew=plan_code != 'free',
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @staticmethod
    def _next_invoice_number(user_id):
        invoice_count = BillingInvoice.query.filter_by(user_id=user_id).count() + 1
        return f'INV-{datetime.now(timezone.utc).strftime("%Y%m")}-{user_id:04d}-{invoice_count:04d}'

    @staticmethod
    def _create_invoice(subscription, description, amount=None, status='paid', issued_at=None, period_start=None, period_end=None):
        issued_value = issued_at or datetime.now(timezone.utc)
        invoice = BillingInvoice(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            invoice_number=SubscriptionService._next_invoice_number(subscription.user_id),
            description=description,
            plan_code=subscription.plan,
            amount=subscription.price_per_month if amount is None else amount,
            currency=subscription.currency or 'USD',
            status=status,
            issued_at=issued_value,
            period_start=period_start,
            period_end=period_end,
            paid_at=issued_value if status == 'paid' else None,
        )
        db.session.add(invoice)
        return invoice

    @staticmethod
    def _seed_invoices(subscription):
        if subscription.invoices.count() > 0:
            return

        issued_at = subscription.current_period_start or subscription.started_at or datetime.now(timezone.utc)

        if subscription.plan == 'free' or (subscription.price_per_month or 0) == 0:
            SubscriptionService._create_invoice(
                subscription,
                description='Free Plan Activated',
                amount=0.0,
                issued_at=issued_at,
                period_start=subscription.started_at,
                period_end=subscription.current_period_end,
            )
            db.session.commit()
            return

        period_end = subscription.current_period_end or subscription.renewal_date or datetime.now(timezone.utc)
        months = 6 if subscription.plan != 'enterprise' else 3
        created_any = False

        for index in range(months):
            invoice_date = period_end - timedelta(days=30 * index)
            if subscription.started_at and invoice_date < subscription.started_at:
                continue

            SubscriptionService._create_invoice(
                subscription,
                description=f'{subscription.plan.title()} Plan Subscription',
                issued_at=invoice_date,
                period_start=invoice_date - timedelta(days=30),
                period_end=invoice_date,
                status='paid' if subscription.is_active else 'pending',
            )
            created_any = True

        if not created_any:
            SubscriptionService._create_invoice(
                subscription,
                description=f'{subscription.plan.title()} Plan Subscription',
                issued_at=issued_at,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                status='paid' if subscription.is_active else 'pending',
            )

        db.session.commit()

    @staticmethod
    def _format_currency(amount, currency='USD'):
        if amount is None:
            return 'Custom'
        symbol = '$' if (currency or 'USD').upper() == 'USD' else f'{currency} '
        return f'{symbol}{amount:.2f}'

    @staticmethod
    def _format_date(value):
        if not value:
            return 'N/A'
        return value.strftime('%Y-%m-%d')

    @staticmethod
    def _serialize_invoice(invoice):
        return {
            'id': invoice.id,
            'date': SubscriptionService._format_date(invoice.issued_at),
            'description': invoice.description,
            'amount': SubscriptionService._format_currency(invoice.amount, invoice.currency),
            'status': invoice.status,
            'invoice': invoice.invoice_number,
            'refundAmount': invoice.refund_amount,
            'failureCode': invoice.failure_code,
            'failureReason': invoice.failure_reason,
            'gatewayReferenceId': invoice.gateway_reference_id,
            'processorEventAt': invoice.processor_event_at.isoformat() if invoice.processor_event_at else None,
            'statusNote': invoice.status_note,
        }

    @staticmethod
    def _usage_rows(user, subscription):
        conversions_total = Conversion.query.filter_by(user_id=user.id).count()
        conversions_used = subscription.conversions_used_this_month or 0
        conversion_limit = subscription.monthly_conversion_limit or 0
        conversion_pct = 0 if conversion_limit <= 0 else min(100, round((conversions_used / conversion_limit) * 100))

        storage_used = float(user.used_gb or 0)
        storage_total = float(subscription.storage_quota_gb or user.quota_gb or 0)
        storage_pct = 0 if storage_total <= 0 else min(100, round((storage_used / storage_total) * 100))

        api_limit = max(1000, int((subscription.monthly_conversion_limit or 100) * 20))
        api_used = min(api_limit, max(conversions_total * 18, conversions_used * 10))
        api_pct = 0 if api_limit <= 0 else min(100, round((api_used / api_limit) * 100))

        return [
            {
                'label': 'Conversions',
                'used': str(conversions_used),
                'total': 'unlimited' if subscription.plan == 'enterprise' else str(conversion_limit),
                'pct': conversion_pct,
            },
            {
                'label': 'Storage',
                'used': f'{storage_used:.1f} GB',
                'total': f'{storage_total:.0f} GB',
                'pct': storage_pct,
            },
            {
                'label': 'API Calls',
                'used': f'{api_used:,}',
                'total': f'{api_limit:,}' if subscription.plan != 'enterprise' else 'custom',
                'pct': api_pct,
            },
        ]

    @staticmethod
    def _billing_history(subscription):
        SubscriptionService._seed_invoices(subscription)
        invoices = subscription.invoices.order_by(BillingInvoice.issued_at.desc()).all()
        return [SubscriptionService._serialize_invoice(invoice) for invoice in invoices]

    @staticmethod
    def _plan_cards(current_plan):
        cards = []
        for plan_id, meta in SubscriptionService.PLAN_CATALOG.items():
            if plan_id == current_plan:
                cta = 'Current Plan'
            elif plan_id == 'enterprise':
                cta = meta['cta']
            elif current_plan == 'free' and plan_id == 'pro':
                cta = 'Upgrade to Pro'
            elif current_plan == 'pro' and plan_id == 'free':
                cta = 'Switch to Free'
            else:
                cta = meta['cta']

            cards.append({
                'id': plan_id,
                'name': meta['name'],
                'price': meta['price'],
                'period': meta['period'],
                'description': meta['description'],
                'features': list(meta['features']),
                'popular': plan_id == 'pro',
                'cta': cta,
                'isCurrent': plan_id == current_plan,
            })
        return cards

    @staticmethod
    def _payment_profile(user, subscription):
        if user.billing_profile:
            profile = user.billing_profile
        else:
            full_name = ' '.join(part for part in [user.first_name, user.last_name] if part).strip() or user.username
            profile = BillingProfile(
                user_id=user.id,
                card_holder=full_name,
                billing_name=full_name,
                billing_line2=user.email,
                billing_country='Not provided',
                tax_exemption='Not applicable',
                payment_status='No payment data available.' if subscription.plan != 'free' else 'No payment method is needed on the free plan.',
            )
            db.session.add(profile)
            db.session.commit()

        full_name = ' '.join(part for part in [user.first_name, user.last_name] if part).strip() or user.username
        has_billing_provider = bool(subscription.stripe_customer_id or subscription.stripe_subscription_id)

        payment = profile.to_payment_dict()
        if subscription.plan == 'free':
            payment['method']['status'] = 'No payment method is needed on the free plan.'
        elif has_billing_provider:
            payment['method']['status'] = 'Payment details are managed by the configured billing provider.'
            if not (profile.card_brand or '').strip() or profile.card_brand == 'No card on file':
                payment['method']['brand'] = 'Managed billing'
                payment['method']['last4'] = 'sync'
                payment['method']['expiry'] = 'N/A'
                payment['method']['holder'] = profile.card_holder or full_name

        return payment

    @staticmethod
    def get_subscription_dashboard(user_id):
        user = User.query.get_or_404(user_id)
        subscription = SubscriptionService._ensure_subscription(user)
        plan_meta = SubscriptionService.PLAN_CATALOG.get(subscription.plan, SubscriptionService.PLAN_CATALOG['free'])
        SubscriptionService._seed_invoices(subscription)

        status = 'cancelled' if subscription.cancelled_at else 'active' if subscription.is_active else 'inactive'
        if subscription.cancelled_at and subscription.current_period_end and subscription.current_period_end > datetime.now(timezone.utc):
            status = 'cancels at period end'

        return {
            'subscription': {
                'plan': plan_meta['name'],
                'status': status,
                'amount': subscription.price_per_month or 0.0,
                'cycle': 'monthly' if plan_meta['period'] == 'month' else plan_meta['period'],
                'startDate': SubscriptionService._format_date(subscription.started_at),
                'nextBilling': SubscriptionService._format_date(subscription.renewal_date),
                'autoRenew': bool(subscription.auto_renew),
                'features': [
                    f'{subscription.storage_quota_gb} GB storage',
                    f'{subscription.max_file_size_mb} MB max file size',
                    *plan_meta['features'],
                ],
                'daysUntilRenewal': subscription.days_until_renewal(),
                'monthlyLimit': subscription.monthly_conversion_limit,
            },
            'usage': SubscriptionService._usage_rows(user, subscription),
            'billingHistory': SubscriptionService._billing_history(subscription),
            'plans': SubscriptionService._plan_cards(subscription.plan),
            'payment': SubscriptionService._payment_profile(user, subscription),
        }

    @staticmethod
    def cancel_subscription(user_id):
        user = User.query.get_or_404(user_id)
        subscription = SubscriptionService._ensure_subscription(user)
        subscription.auto_renew = False
        subscription.cancelled_at = datetime.now(timezone.utc)
        db.session.commit()
        return {
            'message': 'Subscription cancellation scheduled for the end of the current billing period.',
            'subscription': SubscriptionService.get_subscription_dashboard(user_id)['subscription'],
        }

    @staticmethod
    def change_plan(user_id, target_plan):
        plan_code = (target_plan or '').strip().lower()
        if plan_code not in SubscriptionService.PLAN_CATALOG:
            raise ValueError('Unsupported plan selected')
        if plan_code == 'enterprise':
            raise ValueError('Enterprise plan changes require sales assistance')

        user = User.query.get_or_404(user_id)
        subscription = SubscriptionService._ensure_subscription(user)
        if subscription.plan == plan_code:
            raise ValueError('You are already on this plan')

        plan_meta = SubscriptionService.PLAN_CATALOG[plan_code]
        now = datetime.now(timezone.utc)
        old_plan = subscription.plan

        subscription.plan = plan_code
        subscription.storage_quota_gb = plan_meta['storage_quota_gb']
        subscription.monthly_conversion_limit = plan_meta['monthly_conversion_limit']
        subscription.max_file_size_mb = plan_meta['max_file_size_mb']
        subscription.price_per_month = plan_meta['price'] or 0.0
        subscription.currency = 'USD'
        subscription.is_active = True
        subscription.auto_renew = plan_code != 'free'
        subscription.current_period_start = now
        subscription.current_period_end = now + timedelta(days=3650 if plan_code == 'free' else 30)
        subscription.renewal_date = subscription.current_period_end
        subscription.cancelled_at = None

        user.plan = plan_code
        user.quota_gb = plan_meta['storage_quota_gb']

        SubscriptionService._create_invoice(
            subscription,
            description=f'Plan changed from {old_plan.title()} to {plan_code.title()}',
            amount=plan_meta['price'] or 0.0,
            issued_at=now,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            status='paid',
        )

        db.session.commit()
        return {
            'message': f'Plan updated to {plan_meta["name"]}.',
            'dashboard': SubscriptionService.get_subscription_dashboard(user_id),
        }

    @staticmethod
    def render_invoice(invoice_id, user_id):
        invoice = BillingInvoice.query.filter_by(id=invoice_id, user_id=user_id).first_or_404()
        return SubscriptionService._render_invoice_file(invoice)

    @staticmethod
    def render_invoice_for_admin(invoice_id):
        invoice = BillingInvoice.query.filter_by(id=invoice_id).first_or_404()
        return SubscriptionService._render_invoice_file(invoice)

    @staticmethod
    def _render_invoice_file(invoice):
        body = (
            f'Invoice Number: {invoice.invoice_number}\n'
            f'Description: {invoice.description}\n'
            f'Plan: {invoice.plan_code.title()}\n'
            f'Amount: {SubscriptionService._format_currency(invoice.amount, invoice.currency)}\n'
            f'Status: {invoice.status}\n'
            f'Issued At: {SubscriptionService._format_date(invoice.issued_at)}\n'
            f'Billing Period: {SubscriptionService._format_date(invoice.period_start)} to {SubscriptionService._format_date(invoice.period_end)}\n'
        )
        if invoice.status_note:
            body += f'Status Note: {invoice.status_note}\n'
        if invoice.refunded_at:
            body += f'Refunded At: {SubscriptionService._format_date(invoice.refunded_at)}\n'
        if invoice.refund_amount is not None:
            body += f'Refund Amount: {SubscriptionService._format_currency(invoice.refund_amount, invoice.currency)}\n'
        if invoice.failure_code:
            body += f'Failure Code: {invoice.failure_code}\n'
        if invoice.failure_reason:
            body += f'Failure Reason: {invoice.failure_reason}\n'
        if invoice.gateway_reference_id:
            body += f'Gateway Reference: {invoice.gateway_reference_id}\n'
        if invoice.processor_event_at:
            body += f'Processor Event At: {invoice.processor_event_at.strftime("%Y-%m-%d %H:%M")}\n'
        stream = BytesIO(body.encode('utf-8'))
        stream.seek(0)
        return stream, f'{invoice.invoice_number}.txt'