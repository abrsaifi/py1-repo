from flask import Blueprint, request, jsonify, send_file, current_app
import tempfile
import os
import shutil
from pathlib import Path
from app.services.conversions import excel_to_pdf
from app.utils.file_validator import sanitize_filename
from app.services.history import log_history

bp = Blueprint('excel', __name__)


@bp.route('/excel/to-pdf', methods=['POST'])
def excel_to_pdf_route():
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
        safe_name = sanitize_filename(f.filename) or f.filename
        in_path = os.path.join(temp_dir, safe_name)
        f.save(in_path)

        out_name = f"{Path(safe_name).stem}_converted.pdf"
        out_path = os.path.join(temp_dir, out_name)

        ok = excel_to_pdf(in_path, out_path)
        if not ok or not os.path.exists(out_path):
            return jsonify({'success': False, 'error': 'conversion_failed'}), 500

        try:
            log_history(app.config.get('HISTORY_DB', 'conversion_history.db'), 'excel_to_pdf', [f.filename], status='success')
        except Exception:
            pass
        return send_file(out_path, as_attachment=True, download_name=out_name)
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
