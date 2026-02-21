from flask import Blueprint, request, jsonify, send_file, current_app
import tempfile
import os
import shutil
import base64
from app.services.conversions import _generate_preview_from_pdf
from app.services.history import log_history

bp = Blueprint('pdf', __name__)


@bp.route('/pdf/preview', methods=['POST'])
def pdf_preview():
    app = current_app._get_current_object()
    api_key = app.config.get('UPLOAD_API_KEY')
    if api_key:
        provided = request.headers.get('X-API-Key') or request.args.get('api_key')
        if provided != api_key:
            return jsonify({'success': False, 'error': 'unauthorized'}), 401

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({'success': False, 'error': 'no_file'}), 400

    temp_dir = tempfile.mkdtemp()
    try:
        safe_name = f.filename
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''
        if ext != 'pdf':
            return jsonify({'success': False, 'error': 'unsupported_format'}), 400

        img_bytes = _generate_preview_from_pdf(in_path)
        if not img_bytes:
            return jsonify({'success': False, 'error': 'preview_failed'}), 500

        data = base64.b64encode(img_bytes).decode('ascii')
        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'), 'pdf_preview', [f.filename], status='success')
        except Exception:
            pass
        return jsonify({'success': True, 'image': f'data:image/png;base64,{data}'})
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
