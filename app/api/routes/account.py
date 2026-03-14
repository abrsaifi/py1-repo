"""Account management API routes."""
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_file

from app.middleware.auth import auth_required
from app.models import APIKey, BillingProfile, ConnectedApp, User, UserSession, db
from app.services.subscription_service import SubscriptionService

bp = Blueprint('account', __name__, url_prefix='/api/account')

DEFAULT_CONNECTED_APPS = [
    {'provider': 'zapier', 'display_name': 'Zapier', 'icon': '⚙️'},
    {'provider': 'ifttt', 'display_name': 'IFTTT', 'icon': '🔗'},
    {'provider': 'slack', 'display_name': 'Slack', 'icon': '💬'},
]


def _format_relative_time(value):
    if not value:
        return 'Never'

    delta = datetime.now(timezone.utc) - value
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return 'Just now'
    if seconds < 3600:
        minutes = max(seconds // 60, 1)
        return f'{minutes} minute(s) ago'
    if seconds < 86400:
        hours = max(seconds // 3600, 1)
        return f'{hours} hour(s) ago'
    days = max(seconds // 86400, 1)
    return f'{days} day(s) ago'


def _describe_device(user_agent):
    ua = (user_agent or '').lower()
    browser = 'Browser'
    platform = 'Desktop'

    if 'edg' in ua:
        browser = 'Edge'
    elif 'chrome' in ua:
        browser = 'Chrome'
    elif 'firefox' in ua:
        browser = 'Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'

    if 'iphone' in ua:
        platform = 'iPhone'
    elif 'android' in ua:
        platform = 'Android'
    elif 'mac os' in ua or 'macintosh' in ua:
        platform = 'Mac'
    elif 'windows' in ua:
        platform = 'Windows'
    elif 'linux' in ua:
        platform = 'Linux'

    return f'{browser} on {platform}'


def _request_location():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'Unknown location'


def _request_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'Unknown IP'


def _current_user():
    return User.query.get_or_404(request.user_id)


def _ensure_connected_apps(user):
    if user.connected_apps.count():
        return

    for item in DEFAULT_CONNECTED_APPS:
        db.session.add(ConnectedApp(user_id=user.id, **item))
    db.session.commit()


def _ensure_current_session(user):
    active_sessions = user.sessions.filter(UserSession.revoked_at.is_(None)).order_by(UserSession.last_active_at.desc()).all()
    user_agent = request.headers.get('User-Agent', '')
    current_device = _describe_device(user_agent)
    current_ip = _request_ip()

    for session in active_sessions:
        session.is_current = False
        if session.device == current_device and session.ip_address == current_ip:
            session.touch(is_current=True)
            db.session.commit()
            return session

    current_session = UserSession.create_session(
        user_id=user.id,
        device=current_device,
        location=_request_location(),
        ip_address=current_ip,
        is_current=True,
    )
    db.session.add(current_session)
    db.session.commit()
    return current_session


def _ensure_billing_profile(user):
    if user.billing_profile:
        return user.billing_profile

    full_name = ' '.join(part for part in [user.first_name, user.last_name] if part).strip() or user.username
    profile = BillingProfile(
        user_id=user.id,
        card_holder=full_name,
        billing_name=full_name,
        billing_line2=user.email,
        billing_country='Not provided',
        tax_exemption='Not applicable',
        payment_status='No payment data available.',
    )
    db.session.add(profile)
    db.session.commit()
    return profile


def _serialize_api_key(api_key):
    data = api_key.to_dict(include_full_key=False)
    data['last_used'] = _format_relative_time(api_key.last_used_at)
    return data


def _serialize_session(session):
    payload = session.to_dict()
    payload['lastActive'] = _format_relative_time(session.last_active_at)
    return payload


def _serialize_connected_app(app):
    payload = app.to_dict()
    payload['lastUsed'] = _format_relative_time(app.last_used_at)
    return payload


def _serialize_billing_profile(profile):
    payment = profile.to_payment_dict()
    payment['card'] = {
        'brand': profile.card_brand or '',
        'last4': profile.card_last4 or '',
        'expiry_month': profile.card_expiry_month or '',
        'expiry_year': profile.card_expiry_year or '',
        'holder': profile.card_holder or '',
        'status': profile.payment_status or '',
    }
    payment['billingAddressForm'] = {
        'name': profile.billing_name or '',
        'line1': profile.billing_line1 or '',
        'line2': profile.billing_line2 or '',
        'country': profile.billing_country or '',
    }
    payment['taxInfoForm'] = {
        'taxId': profile.tax_id or '',
        'taxExemption': profile.tax_exemption or 'Not applicable',
    }
    return payment


@bp.route('/settings', methods=['GET'])
@auth_required
def get_account_settings():
    user = _current_user()
    _ensure_connected_apps(user)
    _ensure_current_session(user)
    billing_profile = _ensure_billing_profile(user)

    sessions = user.sessions.filter(UserSession.revoked_at.is_(None)).order_by(UserSession.last_active_at.desc()).all()
    api_keys = user.api_keys.order_by(APIKey.created_at.desc()).all()
    connected_apps = user.connected_apps.order_by(ConnectedApp.display_name.asc()).all()

    return jsonify({
        'user': user.to_dict(),
        'preferences': {
            'two_factor_enabled': bool(user.two_factor_enabled),
            'analytics_opt_in': bool(user.analytics_opt_in),
            'marketing_opt_in': bool(user.marketing_opt_in),
            'personalization_opt_in': bool(user.personalization_opt_in),
            'deletion_requested_at': user.deletion_requested_at.isoformat() if user.deletion_requested_at else None,
        },
        'sessions': [_serialize_session(item) for item in sessions],
        'api_keys': [_serialize_api_key(item) for item in api_keys],
        'connected_apps': [_serialize_connected_app(item) for item in connected_apps],
        'billing_profile': _serialize_billing_profile(billing_profile),
    }), 200


@bp.route('/change-password', methods=['POST'])
@auth_required
def change_password():
    user = _current_user()
    payload = request.get_json(silent=True) or {}
    current_password = payload.get('current_password', '')
    new_password = payload.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password are required'}), 400
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'}), 200


@bp.route('/preferences', methods=['POST'])
@auth_required
def update_preferences():
    user = _current_user()
    payload = request.get_json(silent=True) or {}
    allowed = {
        'two_factor_enabled': 'two_factor_enabled',
        'analytics_opt_in': 'analytics_opt_in',
        'marketing_opt_in': 'marketing_opt_in',
        'personalization_opt_in': 'personalization_opt_in',
    }

    updated = {}
    for source_key, attr in allowed.items():
        if source_key in payload:
            setattr(user, attr, bool(payload[source_key]))
            updated[source_key] = bool(getattr(user, attr))

    if not updated:
        return jsonify({'error': 'No valid preferences supplied'}), 400

    db.session.commit()
    return jsonify({'message': 'Preferences updated', 'preferences': updated}), 200


@bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@auth_required
def revoke_session(session_id):
    user = _current_user()
    session_record = user.sessions.filter_by(id=session_id).first()
    if not session_record:
        return jsonify({'error': 'Session not found'}), 404
    if session_record.is_current:
        return jsonify({'error': 'Use the main logout flow to end your current session'}), 400

    session_record.revoke()
    db.session.commit()
    return jsonify({'message': 'Session revoked successfully'}), 200


@bp.route('/api-keys', methods=['POST'])
@auth_required
def create_api_key():
    user = _current_user()
    payload = request.get_json(silent=True) or {}
    name = (payload.get('name') or '').strip() or f'Generated Key {user.api_keys.count() + 1}'
    scopes = payload.get('scopes') or ['conversions:read', 'conversions:write']

    api_key = APIKey.create_key(user.id, name=name, scopes=scopes)
    db.session.add(api_key)
    db.session.commit()

    return jsonify({
        'message': 'API key created successfully',
        'api_key': api_key.to_dict(include_full_key=True),
    }), 201


@bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@auth_required
def delete_api_key(key_id):
    user = _current_user()
    api_key = user.api_keys.filter_by(id=key_id).first()
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404

    db.session.delete(api_key)
    db.session.commit()
    return jsonify({'message': 'API key deleted successfully'}), 200


@bp.route('/apps/<int:app_id>/toggle', methods=['POST'])
@auth_required
def toggle_connected_app(app_id):
    user = _current_user()
    app_record = user.connected_apps.filter_by(id=app_id).first()
    if not app_record:
        return jsonify({'error': 'Connected app not found'}), 404

    app_record.is_connected = not app_record.is_connected
    app_record.last_used_at = datetime.now(timezone.utc) if app_record.is_connected else None
    db.session.commit()

    return jsonify({
        'message': 'Connected app updated successfully',
        'connected_app': _serialize_connected_app(app_record),
    }), 200


@bp.route('/delete-request', methods=['POST'])
@auth_required
def request_account_deletion():
    user = _current_user()
    if not user.deletion_requested_at:
        user.deletion_requested_at = datetime.now(timezone.utc)
        db.session.commit()

    return jsonify({
        'message': 'Account deletion request recorded. Support will follow up shortly.',
        'requested_at': user.deletion_requested_at.isoformat() if user.deletion_requested_at else None,
    }), 200


@bp.route('/billing-profile', methods=['POST'])
@auth_required
def update_billing_profile():
    user = _current_user()
    profile = _ensure_billing_profile(user)
    payload = request.get_json(silent=True) or {}

    card = payload.get('card') or {}
    billing_address = payload.get('billingAddress') or {}
    tax_info = payload.get('taxInfo') or {}

    if 'brand' in card:
        profile.card_brand = (card.get('brand') or '').strip() or 'No card on file'
    if 'last4' in card:
        last4 = ''.join(ch for ch in str(card.get('last4') or '') if ch.isdigit())[-4:]
        profile.card_last4 = last4 or '----'
    if 'expiry_month' in card:
        month = str(card.get('expiry_month') or '').strip()
        profile.card_expiry_month = int(month) if month.isdigit() else None
    if 'expiry_year' in card:
        year = str(card.get('expiry_year') or '').strip()
        profile.card_expiry_year = int(year) if year.isdigit() else None
    if 'holder' in card:
        profile.card_holder = (card.get('holder') or '').strip()
    if 'status' in card:
        profile.payment_status = (card.get('status') or '').strip() or 'Payment details updated manually.'

    if 'name' in billing_address:
        profile.billing_name = (billing_address.get('name') or '').strip()
    if 'line1' in billing_address:
        profile.billing_line1 = (billing_address.get('line1') or '').strip()
    if 'line2' in billing_address:
        profile.billing_line2 = (billing_address.get('line2') or '').strip()
    if 'country' in billing_address:
        profile.billing_country = (billing_address.get('country') or '').strip()

    if 'taxId' in tax_info:
        profile.tax_id = (tax_info.get('taxId') or '').strip()
    if 'taxExemption' in tax_info:
        profile.tax_exemption = (tax_info.get('taxExemption') or '').strip() or 'Not applicable'

    db.session.commit()
    return jsonify({
        'message': 'Billing profile updated successfully',
        'billing_profile': _serialize_billing_profile(profile),
    }), 200


@bp.route('/subscription', methods=['GET'])
@auth_required
def get_subscription_dashboard():
    return jsonify(SubscriptionService.get_subscription_dashboard(request.user_id)), 200


@bp.route('/subscription/cancel', methods=['POST'])
@auth_required
def cancel_subscription():
    return jsonify(SubscriptionService.cancel_subscription(request.user_id)), 200


@bp.route('/subscription/change-plan', methods=['POST'])
@auth_required
def change_subscription_plan():
    payload = request.get_json(silent=True) or {}
    try:
        result = SubscriptionService.change_plan(request.user_id, payload.get('target_plan'))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    return jsonify(result), 200


@bp.route('/invoices/<int:invoice_id>/download', methods=['GET'])
@auth_required
def download_invoice(invoice_id):
    stream, filename = SubscriptionService.render_invoice(invoice_id, request.user_id)
    return send_file(stream, as_attachment=True, download_name=filename, mimetype='text/plain')