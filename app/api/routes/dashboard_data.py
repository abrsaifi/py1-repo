"""Live user and admin dashboard API routes."""
from io import BytesIO
from datetime import datetime, timedelta, timezone
import os
import zipfile

from flask import Blueprint, jsonify, request, send_file

from app.models import Conversion, User, db
from app.middleware.auth import admin_required, auth_required
from app.services.dashboard_service import DashboardService

bp = Blueprint('dashboard_data', __name__, url_prefix='/api/dashboard')


def _get_owned_conversion(user_id, conversion_id):
    user = User.query.get_or_404(user_id)
    conversion = Conversion.query.get_or_404(conversion_id)

    if conversion.user_id != user.id and not user.is_admin():
        return None, user

    return conversion, user


@bp.route('/user', methods=['GET'])
@auth_required
def user_dashboard():
    return jsonify(DashboardService.get_user_dashboard(request.user_id)), 200


@bp.route('/admin-overview', methods=['GET'])
@admin_required
def admin_overview():
    return jsonify(DashboardService.get_admin_overview()), 200


@bp.route('/conversions/<int:conversion_id>/download', methods=['GET'])
@auth_required
def download_conversion(conversion_id):
    conversion, user = _get_owned_conversion(request.user_id, conversion_id)
    if not conversion:
        return jsonify({'error': 'Forbidden'}), 403

    resolved_output_path = DashboardService.resolve_output_path(conversion.output_path)
    if not resolved_output_path or not os.path.exists(resolved_output_path):
        return jsonify({'error': 'File not available for download'}), 404

    conversion.is_downloaded = True
    conversion.download_count = (conversion.download_count or 0) + 1
    db.session.commit()

    download_name = conversion.output_filename or os.path.basename(resolved_output_path)
    return send_file(resolved_output_path, as_attachment=True, download_name=download_name)


@bp.route('/conversions/download-all', methods=['GET'])
@auth_required
def download_all_conversions():
    user = User.query.get_or_404(request.user_id)
    conversions = Conversion.query.filter_by(user_id=user.id, status='completed').order_by(Conversion.created_at.desc()).all()
    downloadable = []
    for item in conversions:
        resolved_output_path = DashboardService.resolve_output_path(item.output_path)
        if resolved_output_path and os.path.exists(resolved_output_path):
            downloadable.append((item, resolved_output_path))

    if not downloadable:
        return jsonify({'error': 'No downloaded files available'}), 404

    archive = BytesIO()
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item, resolved_output_path in downloadable:
            filename = item.output_filename or os.path.basename(resolved_output_path)
            zf.write(resolved_output_path, arcname=filename)
            item.is_downloaded = True
            item.download_count = (item.download_count or 0) + 1

    db.session.commit()
    archive.seek(0)

    return send_file(
        archive,
        as_attachment=True,
        download_name='docpro-conversions.zip',
        mimetype='application/zip',
    )


@bp.route('/conversions/cleanup-old', methods=['POST'])
@auth_required
def cleanup_old_conversions():
    user = User.query.get_or_404(request.user_id)
    payload = request.get_json(silent=True) or {}
    older_than_days = max(int(payload.get('older_than_days', 7)), 1)
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)

    conversions = Conversion.query.filter_by(user_id=user.id, status='completed').all()
    deleted_files = 0
    stale_records = 0

    for conversion in conversions:
        reference_time = conversion.completed_at or conversion.created_at or datetime.now(timezone.utc)
        if reference_time > cutoff:
            continue

        resolved_output_path = DashboardService.resolve_output_path(conversion.output_path)
        if resolved_output_path and os.path.exists(resolved_output_path):
            try:
                os.remove(resolved_output_path)
                deleted_files += 1
            except OSError:
                continue
        else:
            stale_records += 1

        conversion.output_path = None
        conversion.is_downloaded = True

    db.session.commit()

    return jsonify({
        'message': f'Cleaned {deleted_files} old file(s)',
        'deleted_files': deleted_files,
        'stale_records': stale_records,
        'older_than_days': older_than_days,
    }), 200